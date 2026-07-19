from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from ..constants import PaymentMethod


class ExpensePayment(models.Model):
    expense = models.ForeignKey(
        "Expense",
        on_delete=models.CASCADE,
        related_name="payments",
    )
    amount_paid = models.DecimalField(max_digits=15, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.CHOICES,
        blank=True,
    )
    reference = models.CharField(max_length=200, blank=True)
    paid_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="expense_payments",
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-payment_date"]
        verbose_name = _("Expense payment")
        verbose_name_plural = _("Expense payments")

    def __str__(self):
        return f"{self.expense} - {self.amount_paid}"
