from django.test import TestCase
from ..workflows import ExpenseWorkflow
from ..exceptions import WorkflowError
from ..constants import ExpenseStatus


class ExpenseWorkflowTests(TestCase):
    def test_valid_transitions(self):
        self.assertTrue(
            ExpenseWorkflow.is_allowed(ExpenseStatus.DRAFT, ExpenseStatus.SUBMITTED)
        )
        self.assertTrue(
            ExpenseWorkflow.is_allowed(
                ExpenseStatus.SUBMITTED, ExpenseStatus.PENDING_APPROVAL
            )
        )
        self.assertTrue(
            ExpenseWorkflow.is_allowed(
                ExpenseStatus.PENDING_APPROVAL, ExpenseStatus.APPROVED
            )
        )
        self.assertTrue(
            ExpenseWorkflow.is_allowed(
                ExpenseStatus.PENDING_APPROVAL, ExpenseStatus.REJECTED
            )
        )
        self.assertTrue(
            ExpenseWorkflow.is_allowed(ExpenseStatus.APPROVED, ExpenseStatus.PAID)
        )
        self.assertTrue(
            ExpenseWorkflow.is_allowed(ExpenseStatus.PAID, ExpenseStatus.ARCHIVED)
        )

    def test_cancel_from_any_state(self):
        cancelable = [
            ExpenseStatus.DRAFT,
            ExpenseStatus.SUBMITTED,
            ExpenseStatus.PENDING_APPROVAL,
            ExpenseStatus.APPROVED,
            ExpenseStatus.REJECTED,
        ]
        for state in cancelable:
            self.assertTrue(
                ExpenseWorkflow.is_allowed(state, ExpenseStatus.CANCELLED),
                f"Cannot cancel from {state}",
            )

    def test_cannot_cancel_when_paid(self):
        self.assertFalse(
            ExpenseWorkflow.is_allowed(ExpenseStatus.PAID, ExpenseStatus.CANCELLED)
        )

    def test_cannot_cancel_when_archived(self):
        self.assertFalse(
            ExpenseWorkflow.is_allowed(
                ExpenseStatus.ARCHIVED, ExpenseStatus.CANCELLED
            )
        )

    def test_assert_allowed_raises(self):
        with self.assertRaises(WorkflowError):
            ExpenseWorkflow.assert_allowed(ExpenseStatus.DRAFT, ExpenseStatus.PAID)

    def test_next_statuses(self):
        next_states = ExpenseWorkflow.next_statuses(ExpenseStatus.DRAFT)
        self.assertIn(ExpenseStatus.SUBMITTED, next_states)
        self.assertIn(ExpenseStatus.CANCELLED, next_states)

    def test_requires_permission(self):
        self.assertEqual(
            ExpenseWorkflow.requires_permission(ExpenseStatus.APPROVED),
            "expenses.approve_expense",
        )
        self.assertEqual(
            ExpenseWorkflow.requires_permission(ExpenseStatus.PAID),
            "expenses.pay_expense",
        )
        self.assertIsNone(
            ExpenseWorkflow.requires_permission(ExpenseStatus.SUBMITTED)
        )
