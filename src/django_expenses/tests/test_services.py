from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import Expense, ExpenseCategory, ExpenseType, ExpensePayment
from ..services import ExpenseService
from ..exceptions import WorkflowError

User = get_user_model()


class ExpenseServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("testuser", password="testpass")
        cls.approver = User.objects.create_user("approver", password="testpass")
        cls.admin = User.objects.create_superuser(
            "admin", "admin@test.com", "testpass"
        )
        cls.category = ExpenseCategory.objects.create(name="Transport")
        cls.expense_type = ExpenseType.objects.create(
            name="Carburant", category=cls.category
        )

    def test_create_expense(self):
        expense = ExpenseService.create(
            {
                "user": self.user,
                "expense_type": self.expense_type,
                "amount": 50000,
                "description": "Test",
                "date_incurred": "2026-07-01",
            },
            user=self.user,
        )
        self.assertEqual(expense.status, Expense.Status.DRAFT)
        self.assertEqual(expense.amount, 50000)

    def test_submit_expense(self):
        expense = ExpenseService.create(
            {
                "user": self.user,
                "expense_type": self.expense_type,
                "amount": 50000,
                "description": "Test",
                "date_incurred": "2026-07-01",
            },
            user=self.user,
        )
        expense = ExpenseService.submit(expense, user=self.user)
        self.assertEqual(expense.status, Expense.Status.SUBMITTED)

    def test_approve_expense(self):
        expense = ExpenseService.create(
            {
                "user": self.user,
                "expense_type": self.expense_type,
                "amount": 50000,
                "description": "Test",
                "date_incurred": "2026-07-01",
            },
            user=self.user,
        )
        expense = ExpenseService.submit(expense, user=self.user)
        expense.status = Expense.Status.PENDING_APPROVAL
        expense.save()
        expense = ExpenseService.approve(expense, user=self.admin, comment="OK")
        self.assertEqual(expense.status, Expense.Status.APPROVED)

    def test_reject_expense(self):
        expense = ExpenseService.create(
            {
                "user": self.user,
                "expense_type": self.expense_type,
                "amount": 50000,
                "description": "Test",
                "date_incurred": "2026-07-01",
            },
            user=self.user,
        )
        expense = ExpenseService.submit(expense, user=self.user)
        expense.status = Expense.Status.PENDING_APPROVAL
        expense.save()
        expense = ExpenseService.reject(
            expense, user=self.admin, reason="Pas justifié"
        )
        self.assertEqual(expense.status, Expense.Status.REJECTED)
        self.assertEqual(expense.rejection_reason, "Pas justifié")

    def test_pay_expense(self):
        expense = ExpenseService.create(
            {
                "user": self.user,
                "expense_type": self.expense_type,
                "amount": 50000,
                "description": "Test",
                "date_incurred": "2026-07-01",
            },
            user=self.user,
        )
        expense.status = Expense.Status.APPROVED
        expense.save()
        expense = ExpenseService.pay(
            expense,
            user=self.admin,
            payment_data={"payment_method": "cash", "amount_paid": 50000},
        )
        self.assertEqual(expense.status, Expense.Status.PAID)
        self.assertEqual(expense.payments.count(), 1)

    def test_cancel_expense(self):
        expense = ExpenseService.create(
            {
                "user": self.user,
                "expense_type": self.expense_type,
                "amount": 50000,
                "description": "Test",
                "date_incurred": "2026-07-01",
            },
            user=self.user,
        )
        expense = ExpenseService.cancel(expense, user=self.user)
        self.assertEqual(expense.status, Expense.Status.CANCELLED)

    def test_invalid_transition_raises(self):
        expense = ExpenseService.create(
            {
                "user": self.user,
                "expense_type": self.expense_type,
                "amount": 50000,
                "description": "Test",
                "date_incurred": "2026-07-01",
            },
            user=self.user,
        )
        with self.assertRaises(WorkflowError):
            ExpenseService.approve(expense, user=self.admin)
