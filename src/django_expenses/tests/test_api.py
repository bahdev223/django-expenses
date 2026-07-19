from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from ..models import ExpenseCategory

User = get_user_model()


class ExpenseAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("testuser", password="testpass")
        cls.admin = User.objects.create_superuser(
            "admin", "admin@test.com", "testpass"
        )
        cls.category = ExpenseCategory.objects.create(
            code="FUEL", name="Carburant"
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

    def test_list_expenses(self):
        response = self.client.get("/api/expenses/")
        self.assertEqual(response.status_code, 200)

    def test_create_expense(self):
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
        self.assertEqual(response.data["amount"], "50000.00")

    def test_submit_expense(self):
        resp = self.client.post(
            "/api/expenses/",
            {
                "category": self.category.id,
                "amount": 50000,
                "description": "Test submit",
                "date_incurred": "2026-07-01",
            },
            format="json",
        )
        pk = resp.data["id"]
        response = self.client.post(f"/api/expenses/{pk}/submit/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "submitted")
