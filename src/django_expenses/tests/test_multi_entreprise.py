from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError
from django.test import TestCase

from ..models import (
    AvanceDepense,
    BudgetDepense,
    CostCenter,
    ExpenseCategory,
)
from ..services import AvanceService, BudgetService, ExpenseService
from ..settings import EXPENSES
from ..tenancy import (
    ContexteEntreprise,
    filtrer_par_entreprise,
    resoudre_entreprise,
)

User = get_user_model()


class DummyRequest:
    pass


class MultiEntrepriseTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("tenant-user", password="x")
        self.admin = User.objects.create_superuser("tenant-admin", "admin@test.com", "x")
        self.ctx_a = ContexteEntreprise("saheltech", "ENT-A", "Entreprise A")
        self.ctx_b = ContexteEntreprise("saheltech", "ENT-B", "Entreprise B")

    def categorie(self, ctx, code="CARBURANT"):
        return ExpenseCategory.objects.create(
            entreprise_source=ctx.source,
            entreprise_reference=ctx.reference,
            entreprise_libelle=ctx.libelle,
            code=code,
            name=code.title(),
            requires_receipt=False,
            requires_vendor=False,
        )

    def test_same_category_code_is_allowed_in_two_companies(self):
        self.categorie(self.ctx_a)
        self.categorie(self.ctx_b)
        self.assertEqual(
            ExpenseCategory.objects.filter(code="CARBURANT").count(),
            2,
        )

    def test_same_cost_center_code_is_allowed_in_two_companies(self):
        CostCenter.objects.create(
            entreprise_source=self.ctx_a.source,
            entreprise_reference=self.ctx_a.reference,
            code="ADMIN",
            name="Administration A",
        )
        CostCenter.objects.create(
            entreprise_source=self.ctx_b.source,
            entreprise_reference=self.ctx_b.reference,
            code="ADMIN",
            name="Administration B",
        )
        self.assertEqual(CostCenter.objects.filter(code="ADMIN").count(), 2)

    def test_queryset_scope_never_returns_another_company(self):
        self.categorie(self.ctx_a, "A")
        self.categorie(self.ctx_b, "B")
        qs = filtrer_par_entreprise(ExpenseCategory.objects.all(), self.ctx_a)
        self.assertEqual(list(qs.values_list("code", flat=True)), ["A"])

    def test_global_categories_can_be_shared_explicitly(self):
        ExpenseCategory.objects.create(
            code="GLOBAL",
            name="Globale",
            requires_receipt=False,
            requires_vendor=False,
        )
        self.categorie(self.ctx_b, "B")
        qs = filtrer_par_entreprise(
            ExpenseCategory.objects.all(),
            self.ctx_a,
            include_global=True,
        )
        self.assertEqual(set(qs.values_list("code", flat=True)), {"GLOBAL"})

    def test_resolver_uses_server_side_request_context(self):
        request = DummyRequest()
        request.entreprise = {
            "source": "saheltech",
            "reference": "ENT-A",
            "libelle": "Entreprise A",
        }
        with patch.dict(EXPENSES, {"ENABLE_MULTI_ENTREPRISE": True}):
            contexte = resoudre_entreprise(request)
        self.assertEqual(contexte, self.ctx_a)

    def test_missing_context_is_rejected_when_multi_company_is_enabled(self):
        with patch.dict(EXPENSES, {"ENABLE_MULTI_ENTREPRISE": True}):
            with self.assertRaises(PermissionDenied):
                resoudre_entreprise(DummyRequest())

    def test_expense_rejects_category_from_another_company(self):
        cat_b = self.categorie(self.ctx_b)
        with patch.dict(
            EXPENSES,
            {
                "ENABLE_MULTI_ENTREPRISE": True,
                "ALLOW_GLOBAL_CATEGORIES": True,
            },
        ):
            with self.assertRaises(ValidationError):
                ExpenseService.create(
                    {
                        "entreprise_source": self.ctx_a.source,
                        "entreprise_reference": self.ctx_a.reference,
                        "entreprise_libelle": self.ctx_a.libelle,
                        "user": self.user,
                        "category": cat_b,
                        "amount": 1000,
                        "description": "Dépense croisée",
                        "date_incurred": "2026-10-01",
                    },
                    user=self.user,
                )

    def test_budget_isolation_uses_company_and_project(self):
        cat_a = self.categorie(self.ctx_a)
        cat_b = self.categorie(self.ctx_b)

        budget_a = BudgetDepense.objects.create(
            entreprise_source=self.ctx_a.source,
            entreprise_reference=self.ctx_a.reference,
            entreprise_libelle=self.ctx_a.libelle,
            nom="Budget A",
            date_debut="2026-10-01",
            date_fin="2026-10-31",
            montant_alloue=10000,
            categorie=cat_a,
            projet_source="solarplus",
            projet_reference="PROJ-001",
        )
        depense_b = ExpenseService.create(
            {
                "entreprise_source": self.ctx_b.source,
                "entreprise_reference": self.ctx_b.reference,
                "entreprise_libelle": self.ctx_b.libelle,
                "user": self.user,
                "category": cat_b,
                "amount": 1000,
                "description": "Projet B",
                "date_incurred": "2026-10-01",
                "projet_source": "solarplus",
                "projet_reference": "PROJ-001",
            },
            user=self.user,
        )
        self.assertNotIn(budget_a, BudgetService.budgets_applicables(depense_b))

    def test_advance_reference_is_unique_per_company(self):
        kwargs = dict(
            beneficiaire=self.user,
            montant_accorde=1000,
            date_avance="2026-10-01",
            objet="Mission",
            reference="AV-001",
            cree_par=self.admin,
        )
        AvanceService.creer(
            **kwargs,
            entreprise_source=self.ctx_a.source,
            entreprise_reference=self.ctx_a.reference,
        )
        AvanceService.creer(
            **kwargs,
            entreprise_source=self.ctx_b.source,
            entreprise_reference=self.ctx_b.reference,
        )
        self.assertEqual(AvanceDepense.objects.filter(reference="AV-001").count(), 2)

        with self.assertRaises(IntegrityError):
            AvanceService.creer(
                **kwargs,
                entreprise_source=self.ctx_a.source,
                entreprise_reference=self.ctx_a.reference,
            )

    def test_advance_cannot_be_justified_with_other_company_expense(self):
        cat_b = self.categorie(self.ctx_b)
        avance_a = AvanceService.creer(
            beneficiaire=self.user,
            montant_accorde=5000,
            date_avance="2026-10-01",
            objet="Mission A",
            reference="AV-A",
            cree_par=self.admin,
            entreprise_source=self.ctx_a.source,
            entreprise_reference=self.ctx_a.reference,
        )
        depense_b = ExpenseService.create(
            {
                "entreprise_source": self.ctx_b.source,
                "entreprise_reference": self.ctx_b.reference,
                "user": self.user,
                "category": cat_b,
                "amount": 1000,
                "description": "Dépense B",
                "date_incurred": "2026-10-01",
            },
            user=self.user,
        )
        with self.assertRaises(ValidationError):
            AvanceService.ajouter_justification(
                avance_a,
                montant=1000,
                date_depense="2026-10-01",
                description="Croisement interdit",
                depense=depense_b,
                user=self.user,
            )
