from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class ExpenseApproval(models.Model):
    class Decision(models.TextChoices):
        APPROVED = "approved", _("Approuvée")
        REJECTED = "rejected", _("Rejetée")

    expense = models.ForeignKey(
        "Expense",
        on_delete=models.CASCADE,
        related_name="approvals",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="expense_approvals",
    )
    decision = models.CharField(max_length=10, choices=Decision.choices)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Expense approval")
        verbose_name_plural = _("Expense approvals")

    def __str__(self):
        return f"{self.expense} - {self.get_decision_display()}"
