from decimal import Decimal
from datetime import date
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils import timezone
from django.db import transaction
from django.http import HttpResponse
import csv

from .models import Expense, ExpenseAttachment, ExpenseApproval, ExpensePayment, ExpenseComment
from .workflow import StateMachine, WorkflowError
from .receivers import emit_status_signal
from .signals import (
    expense_created,
    expense_updated,
    expense_submitted,
    expense_approved,
    expense_rejected,
    expense_paid,
    expense_cancelled,
)


class ExpenseService:
    @staticmethod
    @transaction.atomic
    def create(data, user=None):
        expense = Expense.objects.create(**data)
        expense_created.send(sender=Expense, expense=expense, user=user)
        return expense

    @staticmethod
    @transaction.atomic
    def update(expense, data, user=None):
        for key, value in data.items():
            setattr(expense, key, value)
        expense.save()
        expense_updated.send(sender=Expense, expense=expense, user=user)
        return expense

    @staticmethod
    @transaction.atomic
    def submit(expense, user=None):
        _assert_editable(expense)
        state = StateMachine()
        state.assert_allowed(expense.status, "submitted")
        expense.status = Expense.Status.SUBMITTED
        expense.date_submitted = timezone.now()
        expense.save()
        expense_submitted.send(sender=Expense, expense=expense, user=user)
        return expense

    @staticmethod
    @transaction.atomic
    def request_approval(expense, user=None):
        _assert_has_perm(user, "expenses.change_expense")
        state = StateMachine()
        state.assert_allowed(expense.status, "pending_approval")
        expense.status = Expense.Status.PENDING_APPROVAL
        expense.save()
        return expense

    @staticmethod
    @transaction.atomic
    def approve(expense, user=None, comment=""):
        _assert_has_perm(user, "expenses.approve_expense")
        state = StateMachine()
        state.assert_allowed(expense.status, "approved")
        expense.status = Expense.Status.APPROVED
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
        return expense

    @staticmethod
    @transaction.atomic
    def reject(expense, user=None, reason=""):
        _assert_has_perm(user, "expenses.approve_expense")
        state = StateMachine()
        state.assert_allowed(expense.status, "rejected")
        expense.status = Expense.Status.REJECTED
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
        state = StateMachine()
        state.assert_allowed(expense.status, "paid")
        expense.status = Expense.Status.PAID
        expense.date_paid = timezone.now()
        expense.payment_method = (payment_data or {}).get("payment_method", "")
        expense.save()
        ExpensePayment.objects.create(
            expense=expense,
            amount_paid=payment_data.get("amount_paid", expense.total_amount) if payment_data else expense.total_amount,
            payment_date=payment_data.get("payment_date", date.today()) if payment_data else date.today(),
            payment_method=expense.payment_method,
            reference=payment_data.get("reference", "") if payment_data else "",
            paid_by=user,
            notes=payment_data.get("notes", "") if payment_data else "",
        )
        expense_paid.send(sender=Expense, expense=expense, user=user)
        return expense

    @staticmethod
    @transaction.atomic
    def cancel(expense, user=None):
        state = StateMachine()
        state.assert_allowed(expense.status, "cancelled")
        _old = expense.status
        expense.status = Expense.Status.CANCELLED
        expense.save()
        expense_cancelled.send(sender=Expense, expense=expense, user=user)
        return expense

    @staticmethod
    @transaction.atomic
    def archive(expense, user=None):
        state = StateMachine()
        state.assert_allowed(expense.status, "archived")
        expense.status = Expense.Status.ARCHIVED
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

    @staticmethod
    def export_csv(queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=expenses.csv"
        writer = csv.writer(response)
        writer.writerow([
            "Reference", "Date", "Amount", "Currency", "Status",
            "Category", "Type", "Cost Center", "Vendor", "Description",
        ])
        for e in queryset.select_related("expense_type__category", "cost_center"):
            writer.writerow([
                e.reference_number,
                e.date_incurred,
                e.total_amount,
                e.currency,
                e.get_status_display(),
                e.expense_type.category.name if e.expense_type else "",
                e.expense_type.name if e.expense_type else "",
                e.cost_center.name if e.cost_center else "",
                e.vendor,
                e.description[:100],
            ])
        return response

    @staticmethod
    def report(start_date, end_date, cost_center=None):
        qs = Expense.objects.filter(
            date_incurred__gte=start_date, date_incurred__lte=end_date
        )
        if cost_center:
            qs = qs.filter(cost_center=cost_center)
        total = sum(e.total_amount for e in qs)
        by_category = list(qs.total_by_category())
        by_status = {
            label: qs.filter(status=code).count()
            for code, label in Expense.Status.choices
        }
        return {
            "total_expenses": total,
            "count": qs.count(),
            "by_category": by_category,
            "by_status": by_status,
            "start_date": start_date,
            "end_date": end_date,
        }


def _assert_editable(expense):
    if not expense.is_editable:
        raise WorkflowError(
            f"Expense is in status '{expense.get_status_display()}' and cannot be edited."
        )


def _assert_has_perm(user, perm):
    if user and not user.has_perm(perm):
        raise PermissionDenied(f"Missing permission: {perm}")
