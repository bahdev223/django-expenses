from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from rest_framework.test import APIClient

from ..models import ExpenseCategory
from ..constants import ExpenseStatus
from ..services import ExpenseService

User = get_user_model()


class ExpenseAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser("admin", "admin@test.com", "testpass")
        cls.category = ExpenseCategory.objects.create(
            code="FUEL",
            name="Carburant",
            requires_receipt=False,
            requires_vendor=False,
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

    def test_list_expenses(self):
        response = self.client.get("/api/expenses/")
        self.assertEqual(response.status_code, 200)

    def test_create_and_submit_expense(self):
        response = self.client.post(
            "/api/expenses/",
            {
                "category": self.category.id,
                "amount": 50000,
                "description": "Test API",
                "date_incurred": "2026-07-01",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        pk = response.data["id"]
        response = self.client.post(f"/api/expenses/{pk}/submit/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "submitted")

    def test_report_endpoint(self):
        response = self.client.get("/api/expenses/report/?start=2026-07-01&end=2026-07-31")
        self.assertEqual(response.status_code, 200)
        self.assertIn("by_status", response.data)
    def test_approve_action_uses_approve_permission_not_add_permission(self):
        approver = User.objects.create_user("approver", password="x")
        approver.user_permissions.add(
            Permission.objects.get(
                content_type__app_label="django_expenses",
                codename="approve_expense",
            )
        )
        expense = ExpenseService.create(
            {
                "user": self.admin,
                "category": self.category,
                "amount": 10000,
                "description": "Approval",
                "date_incurred": "2026-07-01",
                "status": ExpenseStatus.PENDING_APPROVAL,
            },
            user=self.admin,
        )
        self.client.force_authenticate(user=approver)
        response = self.client.post(f"/api/expenses/{expense.pk}/approve/", {"comment": "OK"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], ExpenseStatus.APPROVED)

