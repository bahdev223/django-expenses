from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _


class AvanceDepense(models.Model):
    entreprise_source = models.CharField(max_length=80, blank=True, db_index=True)
    entreprise_reference = models.CharField(max_length=120, blank=True, db_index=True)
    entreprise_libelle = models.CharField(max_length=240, blank=True)

    class Statut(models.TextChoices):
        OUVERTE = "ouverte", _("Ouverte")
        PARTIELLEMENT_JUSTIFIEE = "partiellement_justifiee", _("Partiellement justifiée")
        JUSTIFIEE = "justifiee", _("Justifiée")
        SOLDEE = "soldee", _("Soldée")
        ANNULEE = "annulee", _("Annulée")

    beneficiaire = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="avances_depenses_recues",
    )
    cree_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="avances_depenses_creees",
    )
    montant_accorde = models.DecimalField(max_digits=15, decimal_places=2)
    date_avance = models.DateField()
    objet = models.CharField(max_length=300)
    statut = models.CharField(max_length=30, choices=Statut.choices, default=Statut.OUVERTE)
    reference = models.CharField(max_length=100, db_index=True)
    compte_reference = models.CharField(max_length=120, blank=True)
    notes = models.TextField(blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date_avance", "-cree_le"]
        verbose_name = _("Avance de dépense")
        verbose_name_plural = _("Avances de dépenses")
        constraints = [
            models.CheckConstraint(check=models.Q(montant_accorde__gt=0), name="avance_depense_montant_gt_zero"),
            models.UniqueConstraint(
                fields=["entreprise_source", "entreprise_reference", "reference"],
                name="avance_reference_par_entreprise",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(entreprise_source="", entreprise_reference="")
                    | (~models.Q(entreprise_source="") & ~models.Q(entreprise_reference=""))
                ),
                name="avance_entreprise_coherente",
            ),
        ]

    def __str__(self):
        return f"{self.reference} - {self.beneficiaire} - {self.montant_accorde}"

    @property
    def montant_justifie(self):
        if not self.pk:
            return Decimal("0")
        return self.justifications.aggregate(total=Sum("montant"))["total"] or Decimal("0")

    @property
    def reste_a_justifier(self):
        return max(self.montant_accorde - self.montant_justifie, Decimal("0"))


class JustificationAvance(models.Model):
    avance = models.ForeignKey(
        AvanceDepense,
        on_delete=models.PROTECT,
        related_name="justifications",
    )
    montant = models.DecimalField(max_digits=15, decimal_places=2)
    date_depense = models.DateField()
    description = models.TextField()
    depense = models.OneToOneField(
        "Expense",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="justification_avance",
    )
    piece = models.FileField(upload_to="expenses/advance_receipts/%Y/%m/", blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date_depense", "cree_le"]
        verbose_name = _("Justification d'avance")
        verbose_name_plural = _("Justifications d'avances")
        constraints = [
            models.CheckConstraint(check=models.Q(montant__gt=0), name="justification_avance_montant_gt_zero")
        ]

    def __str__(self):
        return f"{self.avance.reference} - {self.montant}"
