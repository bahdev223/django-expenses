from django.test import TestCase

from ..constants import ExpenseStatus
from ..exceptions import WorkflowError
from ..workflows import ExpenseWorkflow


class ExpenseWorkflowTests(TestCase):
    def test_valid_transitions(self):
        self.assertTrue(ExpenseWorkflow.is_allowed(ExpenseStatus.DRAFT, ExpenseStatus.SUBMITTED))
        self.assertTrue(ExpenseWorkflow.is_allowed(ExpenseStatus.SUBMITTED, ExpenseStatus.PENDING_APPROVAL))
        self.assertTrue(ExpenseWorkflow.is_allowed(ExpenseStatus.PENDING_APPROVAL, ExpenseStatus.APPROVED))
        self.assertTrue(ExpenseWorkflow.is_allowed(ExpenseStatus.PENDING_APPROVAL, ExpenseStatus.REJECTED))
        self.assertTrue(ExpenseWorkflow.is_allowed(ExpenseStatus.APPROVED, ExpenseStatus.PARTIALLY_PAID))
        self.assertTrue(ExpenseWorkflow.is_allowed(ExpenseStatus.APPROVED, ExpenseStatus.PAID))
        self.assertTrue(ExpenseWorkflow.is_allowed(ExpenseStatus.PARTIALLY_PAID, ExpenseStatus.PAID))
        self.assertTrue(ExpenseWorkflow.is_allowed(ExpenseStatus.PAID, ExpenseStatus.ARCHIVED))

    def test_cancel_allowed_only_before_money_moves(self):
        cancelable = [
            ExpenseStatus.DRAFT,
            ExpenseStatus.SUBMITTED,
            ExpenseStatus.PENDING_APPROVAL,
            ExpenseStatus.APPROVED,
            ExpenseStatus.REJECTED,
        ]
        for state in cancelable:
            self.assertTrue(ExpenseWorkflow.is_allowed(state, ExpenseStatus.CANCELLED))
        self.assertFalse(ExpenseWorkflow.is_allowed(ExpenseStatus.PARTIALLY_PAID, ExpenseStatus.CANCELLED))
        self.assertFalse(ExpenseWorkflow.is_allowed(ExpenseStatus.PAID, ExpenseStatus.CANCELLED))
        self.assertFalse(ExpenseWorkflow.is_allowed(ExpenseStatus.ARCHIVED, ExpenseStatus.CANCELLED))

    def test_assert_allowed_raises(self):
        with self.assertRaises(WorkflowError):
            ExpenseWorkflow.assert_allowed(ExpenseStatus.DRAFT, ExpenseStatus.PAID)

    def test_requires_permission_uses_real_app_label(self):
        self.assertEqual(
            ExpenseWorkflow.requires_permission(ExpenseStatus.APPROVED),
            "django_expenses.approve_expense",
        )
        self.assertEqual(
            ExpenseWorkflow.requires_permission(ExpenseStatus.PAID),
            "django_expenses.pay_expense",
        )
