from django.test import TestCase
from ..workflow import StateMachine, WorkflowError


class StateMachineTests(TestCase):
    def test_valid_transitions(self):
        self.assertTrue(StateMachine.is_allowed("draft", "submitted"))
        self.assertTrue(StateMachine.is_allowed("submitted", "pending_approval"))
        self.assertTrue(StateMachine.is_allowed("pending_approval", "approved"))
        self.assertTrue(StateMachine.is_allowed("pending_approval", "rejected"))
        self.assertTrue(StateMachine.is_allowed("approved", "paid"))
        self.assertTrue(StateMachine.is_allowed("paid", "archived"))

    def test_cancel_from_any_state(self):
        for state in ["draft", "submitted", "pending_approval", "approved", "rejected"]:
            self.assertTrue(
                StateMachine.is_allowed(state, "cancelled"),
                f"Cannot cancel from {state}",
            )

    def test_cannot_cancel_when_paid(self):
        self.assertFalse(StateMachine.is_allowed("paid", "cancelled"))

    def test_cannot_cancel_when_archived(self):
        self.assertFalse(StateMachine.is_allowed("archived", "cancelled"))

    def test_assert_allowed_raises(self):
        with self.assertRaises(WorkflowError):
            StateMachine.assert_allowed("draft", "paid")

    def test_next_statuses(self):
        next_states = StateMachine.next_statuses("draft")
        self.assertIn("submitted", next_states)
        self.assertIn("cancelled", next_states)

    def test_requires_permission(self):
        self.assertEqual(StateMachine.requires_permission("approved"), "expenses.approve_expense")
        self.assertEqual(StateMachine.requires_permission("paid"), "expenses.pay_expense")
        self.assertIsNone(StateMachine.requires_permission("submitted"))
