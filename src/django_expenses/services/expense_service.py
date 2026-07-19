from decimal import Decimal
from datetime import date

from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.db import transaction

from ..models import (
    Expense,
    ExpenseAttachment,
    ExpenseApproval,
    ExpensePayment,
    ExpenseComment,
)
from ..constants import ExpenseStatus
from ..exceptions import WorkflowError
from ..workflows import ExpenseWorkflow
from ..signals import (
    expense_created,
    expense_updated,
    expense_submitted,
    expense_approved,
    expense_rejected,
    expense_paid,
    expense_cancelled,
)
from ..hooks import HookRegistry


class ExpenseService:
    """Unified service layer for expense lifecycle management."""

    @staticmethod
    @transaction.atomic
    def create(data, user=None):
        hooks = HookRegistry.get_hooks()
        for hook in hooks:
            data = hook.before_create(data, user) or data
        expense = Expense.objects.create(**data)
        expense_created.send(sender=Expense, expense=expense, user=user)
        for hook in hooks:
            hook.after_create(expense, user)
        return expense

    @staticmethod
    @transaction.atomic
    def update(expense, data, user=None):
        _assert_editable(expense)
        for key, value in data.items():
            setattr(expense, key, value)
        expense.save()
        expense_updated.send(sender=Expense, expense=expense, user=user)
        return expense

    @staticmethod
    @transaction.atomic
    def submit(expense, user=None):
        _assert_editable(expense)
        ExpenseWorkflow.assert_allowed(expense.status, ExpenseStatus.SUBMITTED)
        expense.status = ExpenseStatus.SUBMITTED
        expense.date_submitted = timezone.now()
        expense.save()
        expense_submitted.send(sender=Expense, expense=expense, user=user)
        return expense

    @staticmethod
    @transaction.atomic
    def request_approval(expense, user=None):
        _assert_has_perm(user, "expenses.change_expense")
        ExpenseWorkflow.assert_allowed(expense.status, ExpenseStatus.PENDING_APPROVAL)
        expense.status = ExpenseStatus.PENDING_APPROVAL
        expense.save()
        return expense

    @staticmethod
    @transaction.atomic
    def approve(expense, user=None, comment=""):
        _assert_has_perm(user, "expenses.approve_expense")
        hooks = HookRegistry.get_hooks()
        ExpenseWorkflow.assert_allowed(expense.status, ExpenseStatus.APPROVED)
        for hook in hooks:
            hook.before_transition(expense, ExpenseStatus.APPROVED, user)
        expense.status = ExpenseStatus.APPROVED
        expense.approved_by = user
        expense.date_approved = timezone.now()
        expense.save()
        ExpenseApproval.objects.create(
            expense=expense,
            approved_by=user,
            decision=ExpenseApproval.Decision.APPROVED,
            comment=comment,
        )
        expense_approved.send(sender=Expense, expense=expense, user=user)
        for hook in hooks:
            hook.after_transition(expense, ExpenseStatus.PENDING_APPROVAL, user)
        return expense

    @staticmethod
    @transaction.atomic
    def reject(expense, user=None, reason=""):
        _assert_has_perm(user, "expenses.approve_expense")
        ExpenseWorkflow.assert_allowed(expense.status, ExpenseStatus.REJECTED)
        expense.status = ExpenseStatus.REJECTED
        expense.rejection_reason = reason
        expense.save()
        ExpenseApproval.objects.create(
            expense=expense,
            approved_by=user,
            decision=ExpenseApproval.Decision.REJECTED,
            comment=reason,
        )
        expense_rejected.send(sender=Expense, expense=expense, user=user)
        return expense

    @staticmethod
    @transaction.atomic
    def pay(expense, user=None, payment_data=None):
        _assert_has_perm(user, "expenses.pay_expense")
        hooks = HookRegistry.get_hooks()
        ExpenseWorkflow.assert_allowed(expense.status, ExpenseStatus.PAID)
        pd = payment_data or {}
        for hook in hooks:
            pd = hook.before_pay(expense, pd, user) or pd
        expense.status = ExpenseStatus.PAID
        expense.date_paid = timezone.now()
        expense.payment_method = pd.get("payment_method", "")
        expense.save()
        payment = ExpensePayment.objects.create(
            expense=expense,
            amount_paid=pd.get("amount_paid", expense.total_amount),
            payment_date=pd.get("payment_date", date.today()),
            payment_method=expense.payment_method,
            reference=pd.get("reference", ""),
            paid_by=user,
            notes=pd.get("notes", ""),
        )
        expense_paid.send(sender=Expense, expense=expense, user=user)
        for hook in hooks:
            hook.after_pay(expense, payment, user)
        return expense

    @staticmethod
    @transaction.atomic
    def cancel(expense, user=None):
        ExpenseWorkflow.assert_allowed(expense.status, ExpenseStatus.CANCELLED)
        expense.status = ExpenseStatus.CANCELLED
        expense.save()
        expense_cancelled.send(sender=Expense, expense=expense, user=user)
        return expense

    @staticmethod
    @transaction.atomic
    def archive(expense, user=None):
        ExpenseWorkflow.assert_allowed(expense.status, ExpenseStatus.ARCHIVED)
        expense.status = ExpenseStatus.ARCHIVED
        expense.save()
        return expense

    @staticmethod
    def add_attachment(expense, file, filename, user=None):
        return ExpenseAttachment.objects.create(
            expense=expense, file=file, filename=filename
        )

    @staticmethod
    def add_comment(expense, text, user=None):
        return ExpenseComment.objects.create(
            expense=expense, user=user, comment=text
        )


def _assert_editable(expense):
    if not expense.is_editable:
        raise WorkflowError(
            f"Expense is in status '{expense.get_status_display()}' and cannot be edited."
        )


def _assert_has_perm(user, perm):
    if user and not user.has_perm(perm):
        raise PermissionDenied(f"Missing permission: {perm}")
