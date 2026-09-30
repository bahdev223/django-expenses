from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from ..constants import PaymentMethod


class ExpensePayment(models.Model):
    expense = models.ForeignKey(
        "Expense",
        on_delete=models.PROTECT,
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
    compte_reference = models.CharField(
        max_length=120,
        blank=True,
        help_text=_("External cash/bank/mobile-money account reference, typically from django-comptes."),
    )
    cle_idempotence = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        help_text=_("Optional idempotency key preventing duplicate payment recording."),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-payment_date", "-created_at"]
        verbose_name = _("Expense payment")
        verbose_name_plural = _("Expense payments")
        constraints = [
            models.CheckConstraint(
                check=models.Q(amount_paid__gt=0), name="expense_payment_amount_gt_zero"
            )
        ]

    def clean(self):
        if self.amount_paid is not None and self.amount_paid <= 0:
            raise ValidationError({"amount_paid": _("The payment amount must be greater than zero.")})

    def __str__(self):
        return f"{self.expense} - {self.amount_paid}"

    # Façade française
    depense = property(lambda self: self.expense)
    montant_paye = property(lambda self: self.amount_paid)
    date_paiement = property(lambda self: self.payment_date)
    mode_paiement = property(lambda self: self.payment_method)
    paye_par = property(lambda self: self.paid_by)
