from django.db import models
from django.utils.translation import gettext_lazy as _

from ..constants import ExpenseNature


class ExpenseCategory(models.Model):
    code = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )
    description = models.TextField(blank=True)
    expense_nature = models.CharField(
        max_length=20,
        choices=ExpenseNature.CHOICES,
        blank=True,
        help_text=_("Type of expense: ACHAT, FONCTIONNEMENT, PERSONNEL..."),
    )
    default_account_code = models.CharField(
        max_length=20,
        blank=True,
        help_text=_("OHADA account code (e.g. 6251 for fuel)"),
    )
    default_vat_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text=_("Default VAT rate percentage (e.g. 18.00)"),
    )
    requires_approval = models.BooleanField(
        default=True,
        help_text=_("Whether this expense type requires approval"),
    )
    requires_receipt = models.BooleanField(
        default=True,
        help_text=_("Whether a receipt/justificatif is required"),
    )
    requires_vendor = models.BooleanField(
        default=True,
        help_text=_("Whether a vendor/tiers is required"),
    )
    unit = models.CharField(
        max_length=50, blank=True,
        help_text=_("Default unit of measure (kg, litre, pièce...)"),
    )
    depreciation_rate = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True,
        help_text=_("Annual depreciation rate percentage (for fixed assets)"),
    )
    color = models.CharField(
        max_length=7, blank=True,
        help_text=_("Hex color for UI (e.g. #FF5733)"),
    )
    icon = models.CharField(
        max_length=50, blank=True,
        help_text=_("Font Awesome icon class (e.g. fa-gas-pump)"),
    )
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "code"]
        verbose_name = _("Expense category")
        verbose_name_plural = _("Expense categories")

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} \u203a {self.name}"
        return self.name

    def get_ancestors(self):
        result = []
        node = self
        while node.parent:
            result.append(node.parent)
            node = node.parent
        return list(reversed(result))

    def get_children_recursive(self):
        result = []
        for child in self.children.filter(is_active=True):
            result.append(child)
            result.extend(child.get_children_recursive())
        return result

    def get_full_path(self):
        parts = []
        node = self
        while node:
            parts.append(node.name)
            node = node.parent
        return " / ".join(reversed(parts))

    @property
    def is_leaf(self):
        return not self.children.filter(is_active=True).exists()

    @property
    def depth(self):
        d = 0
        node = self
        while node.parent:
            d += 1
            node = node.parent
        return d

    @property
    def nature_label(self):
        return dict(ExpenseNature.CHOICES).get(self.expense_nature, "")
