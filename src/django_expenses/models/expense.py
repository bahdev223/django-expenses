from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from ..constants import ExpenseStatus, ExpenseNature, PaymentMethod
from ..managers import ExpenseQuerySet


class Expense(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
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
        help_text=_("Nature: operating, investment, mission, purchase..."),
    )
    cost_center = models.ForeignKey(
        "CostCenter",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expenses",
    )
    status = models.CharField(
        max_length=20,
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ExpenseQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Expense")
        verbose_name_plural = _("Expenses")
        permissions = [
            ("approve_expense", _("Can approve expenses")),
            ("pay_expense", _("Can mark expenses as paid")),
            ("view_expense_reports", _("Can view expense reports")),
        ]

    def __str__(self):
        return f"{self.reference_number or '---'} - {self.amount} {self.currency}"

    @property
    def total_amount(self):
        return self.amount + self.tax_amount

    @property
    def is_editable(self):
        return self.status in ExpenseStatus.EDITABLE

    @property
    def suggested_account_code(self):
        if self.category and self.category.default_account_code:
            return self.category.default_account_code
        return ""
