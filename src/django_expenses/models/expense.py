from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _

from ..constants import ExpenseStatus, ExpenseNature, PaymentMethod
from ..managers import ExpenseQuerySet


class Expense(models.Model):
    entreprise_source = models.CharField(max_length=80, blank=True, db_index=True)
    entreprise_reference = models.CharField(max_length=120, blank=True, db_index=True)
    entreprise_libelle = models.CharField(max_length=240, blank=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="expenses",
    )
    category = models.ForeignKey(
        "ExpenseCategory",
        on_delete=models.PROTECT,
        related_name="expenses",
        help_text=_("Hierarchical expense category with default account code"),
    )
    expense_nature = models.CharField(
        max_length=20,
        choices=ExpenseNature.CHOICES,
        blank=True,
        help_text=_("Nature of the expense"),
    )
    cost_center = models.ForeignKey(
        "CostCenter",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expenses",
    )
    projet_source = models.CharField(
        max_length=80,
        blank=True,
        help_text=_("Application/source owning the project, e.g. solarplus or django_projets"),
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
    status = models.CharField(
        max_length=24,
        choices=ExpenseStatus.CHOICES,
        default=ExpenseStatus.DRAFT,
        db_index=True,
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default="XOF")
    description = models.TextField()
    vendor = models.CharField(max_length=300, blank=True)
    date_incurred = models.DateField()
    date_submitted = models.DateTimeField(null=True, blank=True)
    date_approved = models.DateTimeField(null=True, blank=True)
    date_paid = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_expenses",
    )
    rejection_reason = models.TextField(blank=True)
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.CHOICES,
        blank=True,
    )
    reference_number = models.CharField(max_length=100, unique=True, blank=True)
    supprime_le = models.DateTimeField(null=True, blank=True)
    supprime_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="depenses_supprimees",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ExpenseQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Expense")
        verbose_name_plural = _("Expenses")
        permissions = [
            ("approve_expense", _("Can approve expenses")),
            ("pay_expense", _("Can record expense payments")),
            ("view_expense_reports", _("Can view expense reports")),
        ]
        constraints = [
            models.CheckConstraint(check=models.Q(amount__gt=0), name="expense_amount_gt_zero"),
            models.CheckConstraint(check=models.Q(tax_amount__gte=0), name="expense_tax_gte_zero"),
            models.CheckConstraint(
                check=(
                    models.Q(entreprise_source="", entreprise_reference="")
                    | (~models.Q(entreprise_source="") & ~models.Q(entreprise_reference=""))
                ),
                name="expense_entreprise_coherente",
            ),
        ]

    def __str__(self):
        return f"{self.reference_number or '---'} - {self.amount} {self.currency}"

    def clean(self):
        errors = {}
        if self.amount is not None and self.amount <= 0:
            errors["amount"] = _("The amount must be greater than zero.")
        if self.tax_amount is not None and self.tax_amount < 0:
            errors["tax_amount"] = _("The tax amount cannot be negative.")
        if bool(self.projet_source) != bool(self.projet_reference):
            errors["projet_reference"] = _(
                "Project source and project reference must be provided together."
            )
        if bool(self.entreprise_source) != bool(self.entreprise_reference):
            errors["entreprise_reference"] = _(
                "Company source and company reference must be provided together."
            )
        if self.category_id:
            categorie_globale = (
                not self.category.entreprise_source
                and not self.category.entreprise_reference
            )
            meme_entreprise = (
                self.category.entreprise_source == self.entreprise_source
                and self.category.entreprise_reference == self.entreprise_reference
            )
            if not (categorie_globale or meme_entreprise):
                errors["category"] = _("The category belongs to another company.")
        if self.cost_center_id and (
            self.cost_center.entreprise_source != self.entreprise_source
            or self.cost_center.entreprise_reference != self.entreprise_reference
        ):
            errors["cost_center"] = _("The cost center belongs to another company.")
        if errors:
            raise ValidationError(errors)

    @property
    def total_amount(self):
        return (self.amount or Decimal("0")) + (self.tax_amount or Decimal("0"))

    @property
    def paid_amount(self):
        if not self.pk:
            return Decimal("0")
        return self.payments.aggregate(total=Sum("amount_paid"))["total"] or Decimal("0")

    @property
    def remaining_amount(self):
        return max(self.total_amount - self.paid_amount, Decimal("0"))

    @property
    def is_fully_paid(self):
        return self.remaining_amount == 0 and self.total_amount > 0

    @property
    def is_editable(self):
        return self.status in ExpenseStatus.EDITABLE

    @property
    def suggested_account_code(self):
        if self.category and self.category.default_account_code:
            return self.category.default_account_code
        return ""

    # Façade métier française : compatibilité progressive sans migration destructrice.
    entreprise = property(
        lambda self: (
            {
                "source": self.entreprise_source,
                "reference": self.entreprise_reference,
                "libelle": self.entreprise_libelle,
            }
            if self.entreprise_reference else None
        )
    )
    demandeur = property(lambda self: self.user, lambda self, value: setattr(self, "user", value))
    categorie = property(lambda self: self.category, lambda self, value: setattr(self, "category", value))
    nature = property(lambda self: self.expense_nature, lambda self, value: setattr(self, "expense_nature", value))
    centre_cout = property(lambda self: self.cost_center, lambda self, value: setattr(self, "cost_center", value))
    projet = property(
        lambda self: (
            {"source": self.projet_source, "reference": self.projet_reference, "libelle": self.projet_libelle}
            if self.projet_reference else None
        )
    )
    statut = property(lambda self: self.status, lambda self, value: setattr(self, "status", value))
    montant = property(lambda self: self.amount, lambda self, value: setattr(self, "amount", value))
    montant_taxe = property(lambda self: self.tax_amount, lambda self, value: setattr(self, "tax_amount", value))
    montant_total = property(lambda self: self.total_amount)
    montant_paye = property(lambda self: self.paid_amount)
    reste_a_payer = property(lambda self: self.remaining_amount)
    devise = property(lambda self: self.currency, lambda self, value: setattr(self, "currency", value))
    fournisseur = property(lambda self: self.vendor, lambda self, value: setattr(self, "vendor", value))
    date_depense = property(lambda self: self.date_incurred, lambda self, value: setattr(self, "date_incurred", value))
    mode_paiement = property(lambda self: self.payment_method, lambda self, value: setattr(self, "payment_method", value))
    numero_reference = property(lambda self: self.reference_number)
    est_supprimee = property(lambda self: self.supprime_le is not None)
