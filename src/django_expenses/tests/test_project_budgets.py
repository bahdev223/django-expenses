from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from ..constants import ExpenseStatus
from ..models import BudgetDepense, ExpenseCategory
from ..services import BudgetService, ExpenseService

User = get_user_model()


class BudgetProjetTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("projet-user", password="x")
        self.admin = User.objects.create_superuser("projet-admin", "admin@test.com", "x")
        self.category = ExpenseCategory.objects.create(
            code="PROJET",
            name="Dépenses projet",
            requires_receipt=False,
            requires_vendor=False,
        )

    def depense(self, reference, montant=5000, statut=ExpenseStatus.DRAFT):
        depense = ExpenseService.create(
            {
                "user": self.user,
                "category": self.category,
                "amount": montant,
                "description": f"Dépense {reference}",
                "date_incurred": "2026-09-15",
                "projet_source": "solarplus",
                "projet_reference": reference,
                "projet_libelle": f"Projet {reference}",
            },
            user=self.user,
        )
        if statut != ExpenseStatus.DRAFT:
            depense.status = statut
            depense.save(update_fields=["status"])
        return depense

    def test_budget_projet_ne_s_applique_qu_au_bon_projet(self):
        budget_a = BudgetDepense.objects.create(
            nom="Budget projet A",
            date_debut="2026-09-01",
            date_fin="2026-09-30",
            montant_alloue=10000,
            categorie=self.category,
            projet_source="solarplus",
            projet_reference="PROJ-A",
            projet_libelle="Projet A",
        )
        depense_a = self.depense("PROJ-A")
        depense_b = self.depense("PROJ-B")

        self.assertIn(budget_a, BudgetService.budgets_applicables(depense_a))
        self.assertNotIn(budget_a, BudgetService.budgets_applicables(depense_b))

    def test_budget_global_continue_de_s_appliquer_aux_projets(self):
        budget_global = BudgetDepense.objects.create(
            nom="Budget global",
            date_debut="2026-09-01",
            date_fin="2026-09-30",
            montant_alloue=50000,
            categorie=self.category,
        )
        depense = self.depense("PROJ-A")
        self.assertIn(budget_global, BudgetService.budgets_applicables(depense))

    def test_consommation_budget_projet_ignore_les_autres_projets(self):
        budget = BudgetDepense.objects.create(
            nom="Budget projet A",
            date_debut="2026-09-01",
            date_fin="2026-09-30",
            montant_alloue=20000,
            categorie=self.category,
            projet_source="solarplus",
            projet_reference="PROJ-A",
        )
        self.depense("PROJ-A", montant=7000, statut=ExpenseStatus.APPROVED)
        self.depense("PROJ-B", montant=9000, statut=ExpenseStatus.APPROVED)

        self.assertEqual(budget.montant_consomme, Decimal("7000"))
        self.assertEqual(budget.montant_disponible, Decimal("13000"))

    def test_budget_projet_bloque_seulement_son_projet(self):
        BudgetDepense.objects.create(
            nom="Petit budget projet A",
            date_debut="2026-09-01",
            date_fin="2026-09-30",
            montant_alloue=1000,
            categorie=self.category,
            projet_source="solarplus",
            projet_reference="PROJ-A",
            bloquant=True,
        )
        depense_a = self.depense("PROJ-A", montant=2000)
        depense_b = self.depense("PROJ-B", montant=2000)

        with self.assertRaises(ValidationError):
            BudgetService.verifier_depense(depense_a)

        BudgetService.verifier_depense(depense_b)

    def test_source_et_reference_projet_sont_indissociables(self):
        with self.assertRaises(ValidationError):
            ExpenseService.create(
                {
                    "user": self.user,
                    "category": self.category,
                    "amount": 1000,
                    "description": "Projet incomplet",
                    "date_incurred": "2026-09-15",
                    "projet_reference": "PROJ-A",
                },
                user=self.user,
            )
