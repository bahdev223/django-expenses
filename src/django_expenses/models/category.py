from django.db import models
from django.utils.translation import gettext_lazy as _


class ExpenseCategory(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = _("Expense category")
        verbose_name_plural = _("Expense categories")

    def __str__(self):
        return self.name


class ExpenseType(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(
        ExpenseCategory, on_delete=models.CASCADE, related_name="expense_types"
    )
    description = models.TextField(blank=True)
    requires_approval = models.BooleanField(default=True)
    max_amount = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = _("Expense type")
        verbose_name_plural = _("Expense types")

    def __str__(self):
        return self.name
