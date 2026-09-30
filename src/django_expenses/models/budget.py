from decimal import Decimal

from django.db import models
from django.db.models import Q, Sum, F
from django.utils.translation import gettext_lazy as _

from ..constants import ExpenseStatus


class BudgetDepense(models.Model):
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
        if self.categorie_id:
            qs = qs.filter(category_id=self.categorie_id)
        if self.centre_cout_id:
            qs = qs.filter(cost_center_id=self.centre_cout_id)
        return qs

    @property
    def montant_consomme(self):
        return self.depenses_queryset().aggregate(
            total=Sum(F("amount") + F("tax_amount"))
        )["total"] or Decimal("0")

    @property
    def montant_disponible(self):
        return self.montant_alloue - self.montant_consomme
