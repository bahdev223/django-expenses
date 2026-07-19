from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import ExpenseCategory, CostCenter, Expense

User = get_user_model()


class ExpenseModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("testuser", password="testpass")
        cls.parent_cat = ExpenseCategory.objects.create(
            code="TRANSPORT", name="Transport"
        )
        cls.category = ExpenseCategory.objects.create(
            code="FUEL", name="Carburant", parent=cls.parent_cat,
            default_account_code="6251",
        )
        cls.cost_center = CostCenter.objects.create(
            code="ADMIN", name="Administration"
        )

    def test_create_expense(self):
        expense = Expense.objects.create(
            user=self.user,
            category=self.category,
            amount=50000,
            description="Test dépense",
            vendor="Station Total",
            date_incurred="2026-07-01",
        )
        self.assertEqual(expense.status, Expense.Status.DRAFT)
        self.assertEqual(expense.total_amount, 50000)
        self.assertTrue(expense.is_editable)
        self.assertEqual(expense.suggested_account_code, "6251")

    def test_expense_total_with_tax(self):
        expense = Expense.objects.create(
            user=self.user,
            category=self.category,
            amount=50000,
            tax_amount=5000,
            description="Test avec taxe",
            date_incurred="2026-07-01",
        )
        self.assertEqual(expense.total_amount, 55000)

    def test_expense_str(self):
        expense = Expense.objects.create(
            user=self.user,
            category=self.category,
            amount=50000,
            description="Test",
            date_incurred="2026-07-01",
        )
        self.assertIn("50000", str(expense))

    def test_expense_non_editable_when_submitted(self):
        expense = Expense.objects.create(
            user=self.user,
            category=self.category,
            amount=50000,
            description="Test",
            date_incurred="2026-07-01",
            status=Expense.Status.SUBMITTED,
        )
        self.assertFalse(expense.is_editable)

    def test_category_hierarchy(self):
        self.assertEqual(self.category.parent, self.parent_cat)
        self.assertEqual(self.category.get_full_path(), "Transport / Carburant")
        self.assertEqual(self.category.depth, 1)
        self.assertEqual(self.parent_cat.depth, 0)
        self.assertTrue(self.category.is_leaf)
        self.assertFalse(self.parent_cat.is_leaf)
