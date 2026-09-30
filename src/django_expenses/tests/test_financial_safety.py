from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import PermissionDenied, ValidationError
from django.test import TestCase
from django.dispatch import receiver

from ..constants import ExpenseStatus
from ..models import (
    ExpenseCategory,
    ExpensePayment,
    BudgetDepense,
    Depense,
    PaiementDepense,
)
from ..services import ExpenseService, ReportService
from ..signals import expense_created, expense_payment_recorded

User = get_user_model()


class FinancialSafetyTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("normal", password="x")
        self.admin = User.objects.create_superuser("root", "root@test.com", "x")
        self.category = ExpenseCategory.objects.create(
            code="SAFE",
            name="Sécurité",
            requires_receipt=False,
            requires_vendor=False,
        )

    def expense(self, amount=50000):
        return ExpenseService.create(
            {
                "user": self.user,
                "category": self.category,
                "amount": amount,
                "description": "Test",
                "date_incurred": "2026-07-01",
            },
            user=self.user,
        )

    def test_real_permission_label_is_django_expenses(self):
        perm = Permission.objects.get(
            content_type__app_label="django_expenses",
            codename="approve_expense",
        )
        self.user.user_permissions.add(perm)
        self.assertTrue(self.user.has_perm("django_expenses.approve_expense"))
        self.assertFalse(self.user.has_perm("expenses.approve_expense"))

    def test_unauthorized_user_cannot_pay(self):
        expense = self.expense()
        expense.status = ExpenseStatus.APPROVED
        expense.save(update_fields=["status"])
        with self.assertRaises(PermissionDenied):
            ExpenseService.pay(expense, user=self.user)

    def test_overpayment_is_rejected(self):
        expense = self.expense()
        expense.status = ExpenseStatus.APPROVED
        expense.save(update_fields=["status"])
        with self.assertRaises(ValidationError):
            ExpenseService.pay(expense, user=self.admin, payment_data={"amount_paid": 50001})
        self.assertEqual(ExpensePayment.objects.count(), 0)

    def test_idempotency_key_prevents_duplicate_payment(self):
        expense = self.expense()
        expense.status = ExpenseStatus.APPROVED
        expense.save(update_fields=["status"])
        payload = {"amount_paid": 10000, "cle_idempotence": "PAY-001"}
        ExpenseService.pay(expense, user=self.admin, payment_data=payload)
        ExpenseService.pay(expense, user=self.admin, payment_data=payload)
        self.assertEqual(ExpensePayment.objects.count(), 1)

    def test_budget_blocks_approval(self):
        BudgetDepense.objects.create(
            nom="Budget juillet",
            date_debut="2026-07-01",
            date_fin="2026-07-31",
            montant_alloue=10000,
            categorie=self.category,
            bloquant=True,
        )
        expense = self.expense(amount=20000)
        expense.status = ExpenseStatus.PENDING_APPROVAL
        expense.save(update_fields=["status"])
        with self.assertRaises(ValidationError):
            ExpenseService.approve(expense, user=self.admin)

    def test_soft_delete_preserves_record_and_audit(self):
        expense = self.expense()
        ExpenseService.delete(expense, user=self.admin)
        expense.refresh_from_db()
        self.assertEqual(expense.status, ExpenseStatus.CANCELLED)
        self.assertIsNotNone(expense.supprime_le)
        self.assertTrue(expense.evenements.filter(action="suppression_logique").exists())

    def test_report_service_uses_status_constants_without_crashing(self):
        self.expense()
        report = ReportService.generate_report(
            start_date=__import__("datetime").date(2026, 7, 1),
            end_date=__import__("datetime").date(2026, 7, 31),
        )
        self.assertEqual(report["count"], 1)
        self.assertIn("Brouillon", {str(key) for key in report["by_status"].keys()})

    def test_french_model_aliases(self):
        self.assertIs(Depense, __import__("django_expenses.models", fromlist=["Expense"]).Expense)
        self.assertIs(PaiementDepense, ExpensePayment)

    def test_creation_signal_is_emitted_once(self):
        calls = []

        def handler(sender, expense, user, **kwargs):
            calls.append(expense.pk)

        expense_created.connect(handler, dispatch_uid="test_creation_once")
        try:
            self.expense()
        finally:
            expense_created.disconnect(dispatch_uid="test_creation_once")
        self.assertEqual(len(calls), 1)

    def test_payment_signal_emitted_for_each_partial_payment(self):
        calls = []

        def handler(sender, payment, **kwargs):
            calls.append(payment.pk)

        expense_payment_recorded.connect(handler, dispatch_uid="test_payment_each")
        try:
            expense = self.expense()
            expense.status = ExpenseStatus.APPROVED
            expense.save(update_fields=["status"])
            ExpenseService.pay(expense, user=self.admin, payment_data={"amount_paid": 10000})
            ExpenseService.pay(expense, user=self.admin, payment_data={"amount_paid": 40000})
        finally:
            expense_payment_recorded.disconnect(dispatch_uid="test_payment_each")
        self.assertEqual(len(calls), 2)
