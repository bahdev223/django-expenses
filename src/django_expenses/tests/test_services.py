from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from ..constants import ExpenseStatus
from ..exceptions import WorkflowError
from ..models import Expense, ExpenseCategory
from ..services import ExpenseService

User = get_user_model()


class ExpenseServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("testuser", password="testpass")
        cls.admin = User.objects.create_superuser("admin", "admin@test.com", "testpass")
        cls.category = ExpenseCategory.objects.create(
            code="FUEL",
            name="Carburant",
            default_account_code="6251",
            requires_receipt=False,
            requires_vendor=False,
        )

    def create_expense(self, **overrides):
        data = {
            "user": self.user,
            "category": self.category,
            "amount": 50000,
            "description": "Test",
            "date_incurred": "2026-07-01",
        }
        data.update(overrides)
        return ExpenseService.create(data, user=self.user)

    def test_create_expense(self):
        expense = self.create_expense()
        self.assertEqual(expense.status, ExpenseStatus.DRAFT)
        self.assertEqual(expense.amount, 50000)
        self.assertEqual(expense.suggested_account_code, "6251")
        self.assertEqual(expense.evenements.filter(action="creation").count(), 1)

    def test_submit_expense(self):
        expense = self.create_expense()
        expense = ExpenseService.submit(expense, user=self.admin)
        self.assertEqual(expense.status, ExpenseStatus.SUBMITTED)

    def test_submit_requires_receipt_and_vendor_when_category_demands_it(self):
        category = ExpenseCategory.objects.create(
            code="STRICT",
            name="Strict",
            requires_receipt=True,
            requires_vendor=True,
        )
        expense = self.create_expense(category=category, vendor="Fournisseur")
        with self.assertRaises(Exception):
            ExpenseService.submit(expense, user=self.admin)
        ExpenseService.add_attachment(
            expense,
            SimpleUploadedFile("recu.pdf", b"pdf"),
            user=self.admin,
        )
        expense = ExpenseService.submit(expense, user=self.admin)
        self.assertEqual(expense.status, ExpenseStatus.SUBMITTED)

    def test_approve_expense(self):
        expense = self.create_expense()
        expense = ExpenseService.submit(expense, user=self.admin)
        expense = ExpenseService.request_approval(expense, user=self.admin)
        expense = ExpenseService.approve(expense, user=self.admin, comment="OK")
        self.assertEqual(expense.status, ExpenseStatus.APPROVED)
        self.assertEqual(expense.approvals.count(), 1)

    def test_reject_expense(self):
        expense = self.create_expense()
        expense = ExpenseService.submit(expense, user=self.admin)
        expense = ExpenseService.request_approval(expense, user=self.admin)
        expense = ExpenseService.reject(expense, user=self.admin, reason="Pas justifié")
        self.assertEqual(expense.status, ExpenseStatus.REJECTED)
        self.assertEqual(expense.rejection_reason, "Pas justifié")

    def test_partial_then_full_payment(self):
        expense = self.create_expense()
        expense.status = ExpenseStatus.APPROVED
        expense.save(update_fields=["status"])

        expense = ExpenseService.pay(
            expense,
            user=self.admin,
            payment_data={"payment_method": "cash", "amount_paid": 10000},
        )
        self.assertEqual(expense.status, ExpenseStatus.PARTIALLY_PAID)
        self.assertEqual(expense.paid_amount, 10000)
        self.assertEqual(expense.remaining_amount, 40000)

        expense = ExpenseService.pay(
            expense,
            user=self.admin,
            payment_data={"payment_method": "cash", "amount_paid": 40000},
        )
        self.assertEqual(expense.status, ExpenseStatus.PAID)
        self.assertEqual(expense.payments.count(), 2)
        self.assertEqual(expense.remaining_amount, 0)

    def test_invalid_transition_raises(self):
        expense = self.create_expense()
        with self.assertRaises(WorkflowError):
            ExpenseService.approve(expense, user=self.admin)
