from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from ..models import AvanceDepense
from ..services import AvanceService

User = get_user_model()


class AvanceServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("beneficiaire")
        self.admin = User.objects.create_superuser("admin2", "admin2@test.com", "x")
        self.avance = AvanceService.creer(
            beneficiaire=self.user,
            montant_accorde=50000,
            date_avance="2026-07-01",
            objet="Mission terrain",
            reference="AV-001",
            cree_par=self.admin,
            compte_reference="CAISSE-PRINCIPALE",
        )

    def test_partial_then_complete_justification(self):
        AvanceService.ajouter_justification(
            self.avance,
            montant=20000,
            date_depense="2026-07-02",
            description="Transport",
            user=self.admin,
        )
        self.avance.refresh_from_db()
        self.assertEqual(self.avance.statut, AvanceDepense.Statut.PARTIELLEMENT_JUSTIFIEE)
        self.assertEqual(self.avance.reste_a_justifier, 30000)

        AvanceService.ajouter_justification(
            self.avance,
            montant=30000,
            date_depense="2026-07-03",
            description="Hébergement",
            user=self.admin,
        )
        self.avance.refresh_from_db()
        self.assertEqual(self.avance.statut, AvanceDepense.Statut.JUSTIFIEE)
        self.assertEqual(self.avance.reste_a_justifier, 0)

        AvanceService.solder(self.avance, user=self.admin)
        self.avance.refresh_from_db()
        self.assertEqual(self.avance.statut, AvanceDepense.Statut.SOLDEE)

    def test_cannot_overjustify(self):
        with self.assertRaises(ValidationError):
            AvanceService.ajouter_justification(
                self.avance,
                montant=50001,
                date_depense="2026-07-02",
                description="Trop",
                user=self.admin,
            )
