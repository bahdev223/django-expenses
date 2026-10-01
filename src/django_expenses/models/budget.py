from decimal import Decimal

from django.db import models
from django.db.models import Q, Sum, F
from django.utils.translation import gettext_lazy as _

from ..constants import ExpenseStatus


class BudgetDepense(models.Model):
    entreprise_source = models.CharField(max_length=80, blank=True, db_index=True)
    entreprise_reference = models.CharField(max_length=120, blank=True, db_index=True)
    entreprise_libelle = models.CharField(max_length=240, blank=True)
    nom = models.CharField(max_length=200)
    date_debut = models.DateField()
    date_fin = models.DateField()
    montant_alloue = models.DecimalField(max_digits=15, decimal_places=2)
    categorie = models.ForeignKey(
        "ExpenseCategory",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="budgets_depenses",
    )
    centre_cout = models.ForeignKey(
        "CostCenter",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="budgets_depenses",
    )
    projet_source = models.CharField(
        max_length=80,
        blank=True,
        help_text=_("Application/source owning the project"),
    )
    projet_reference = models.CharField(
        max_length=120,
        blank=True,
        db_index=True,
        help_text=_("Stable external project reference"),
    )
    projet_libelle = models.CharField(
        max_length=240,
        blank=True,
        help_text=_("Project label snapshot for display"),
    )
    bloquant = models.BooleanField(default=True)
    actif = models.BooleanField(default=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date_debut", "nom"]
        verbose_name = _("Budget de dépense")
        verbose_name_plural = _("Budgets de dépenses")
        constraints = [
            models.CheckConstraint(check=Q(montant_alloue__gte=0), name="budget_depense_montant_gte_zero"),
            models.CheckConstraint(check=Q(date_fin__gte=F("date_debut")), name="budget_depense_dates_valides"),
            models.CheckConstraint(
                check=(
                    Q(entreprise_source="", entreprise_reference="")
                    | (~Q(entreprise_source="") & ~Q(entreprise_reference=""))
                ),
                name="budget_depense_entreprise_coherente",
            ),
            models.CheckConstraint(
                check=(
                    Q(projet_source="", projet_reference="")
                    | (~Q(projet_source="") & ~Q(projet_reference=""))
                ),
                name="budget_depense_projet_coherent",
            ),
        ]

    def __str__(self):
        return f"{self.nom} - {self.montant_alloue}"

    def depenses_queryset(self):
        qs = self._meta.apps.get_model("django_expenses", "Expense").objects.filter(
            date_incurred__gte=self.date_debut,
            date_incurred__lte=self.date_fin,
            status__in=[
                ExpenseStatus.APPROVED,
                ExpenseStatus.PARTIALLY_PAID,
                ExpenseStatus.PAID,
                ExpenseStatus.ARCHIVED,
            ],
        )
        qs = qs.filter(
            entreprise_source=self.entreprise_source,
            entreprise_reference=self.entreprise_reference,
        )
        if self.categorie_id:
            qs = qs.filter(category_id=self.categorie_id)
        if self.centre_cout_id:
            qs = qs.filter(cost_center_id=self.centre_cout_id)
        if self.projet_reference:
            qs = qs.filter(
                projet_source=self.projet_source,
                projet_reference=self.projet_reference,
            )
        return qs

    def clean(self):
        from django.core.exceptions import ValidationError

        errors = {}
        if bool(self.entreprise_source) != bool(self.entreprise_reference):
            errors["entreprise_reference"] = (
                "entreprise_source et entreprise_reference doivent être renseignés ensemble."
            )
        if self.categorie_id:
            categorie_globale = self.categorie.est_globale
            meme_entreprise = (
                self.categorie.entreprise_source == self.entreprise_source
                and self.categorie.entreprise_reference == self.entreprise_reference
            )
            if not (categorie_globale or meme_entreprise):
                errors["categorie"] = "La catégorie appartient à une autre entreprise."
        if self.centre_cout_id and (
            self.centre_cout.entreprise_source != self.entreprise_source
            or self.centre_cout.entreprise_reference != self.entreprise_reference
        ):
            errors["centre_cout"] = "Le centre de coût appartient à une autre entreprise."
        if errors:
            raise ValidationError(errors)

    @property
    def est_budget_projet(self):
        return bool(self.projet_reference)

    @property
    def projet(self):
        if not self.projet_reference:
            return None
        return {
            "source": self.projet_source,
            "reference": self.projet_reference,
            "libelle": self.projet_libelle,
        }

    @property
    def montant_consomme(self):
        return self.depenses_queryset().aggregate(
            total=Sum(F("amount") + F("tax_amount"))
        )["total"] or Decimal("0")

    @property
    def montant_disponible(self):
        return self.montant_alloue - self.montant_consomme
