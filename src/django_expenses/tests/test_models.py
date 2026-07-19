from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import ExpenseCategory, ExpenseType, CostCenter, Expense

User = get_user_model()


class ExpenseModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("testuser", password="testpass")
        cls.category = ExpenseCategory.objects.create(name="Transport")
        cls.expense_type = ExpenseType.objects.create(
            name="Carburant", category=cls.category
        )
        cls.cost_center = CostCenter.objects.create(
            code="ADMIN", name="Administration"
        )

    def test_create_expense(self):
        expense = Expense.objects.create(
            user=self.user,
            expense_type=self.expense_type,
            amount=50000,
            description="Test dépense",
            vendor="Station Total",
            date_incurred="2026-07-01",
        )
        self.assertEqual(expense.status, Expense.Status.DRAFT)
        self.assertEqual(expense.total_amount, 50000)
        self.assertTrue(expense.is_editable)

    def test_expense_total_with_tax(self):
        expense = Expense.objects.create(
            user=self.user,
            expense_type=self.expense_type,
            amount=50000,
            tax_amount=5000,
            description="Test avec taxe",
            date_incurred="2026-07-01",
        )
        self.assertEqual(expense.total_amount, 55000)

    def test_expense_str(self):
        expense = Expense.objects.create(
            user=self.user,
            expense_type=self.expense_type,
            amount=50000,
            description="Test",
            date_incurred="2026-07-01",
        )
        self.assertIn("50000", str(expense))

    def test_expense_non_editable_when_submitted(self):
        expense = Expense.objects.create(
            user=self.user,
            expense_type=self.expense_type,
            amount=50000,
            description="Test",
            date_incurred="2026-07-01",
            status=Expense.Status.SUBMITTED,
        )
        self.assertFalse(expense.is_editable)
