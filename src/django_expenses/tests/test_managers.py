from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import Expense, ExpenseCategory, ExpenseType

User = get_user_model()


class ExpenseQuerySetTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("testuser", password="testpass")
        cls.category = ExpenseCategory.objects.create(name="Transport")
        cls.expense_type = ExpenseType.objects.create(
            name="Carburant", category=cls.category
        )
        Expense.objects.create(
            user=cls.user,
            expense_type=cls.expense_type,
            amount=10000,
            description="Draft",
            date_incurred="2026-07-01",
            status=Expense.Status.DRAFT,
        )
        Expense.objects.create(
            user=cls.user,
            expense_type=cls.expense_type,
            amount=20000,
            description="Paid",
            date_incurred="2026-07-02",
            status=Expense.Status.PAID,
        )
        Expense.objects.create(
            user=cls.user,
            expense_type=cls.expense_type,
            amount=30000,
            description="Approved",
            date_incurred="2026-07-03",
            status=Expense.Status.APPROVED,
        )

    def test_by_status(self):
        self.assertEqual(Expense.objects.by_status("draft").count(), 1)
        self.assertEqual(Expense.objects.by_status("paid").count(), 1)

    def test_by_user(self):
        self.assertEqual(Expense.objects.by_user(self.user).count(), 3)

    def test_editable(self):
        self.assertEqual(Expense.objects.editable().count(), 1)

    def test_paid(self):
        self.assertEqual(Expense.objects.paid().count(), 1)

    def test_total_amount(self):
        total = Expense.objects.total_amount()
        self.assertEqual(total, 60000)
