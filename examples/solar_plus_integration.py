"""Example integration with accounting and treasury engines.

Accounting and treasury are intentionally separate:
- approval can trigger an accounting recognition entry;
- every recorded payment triggers exactly one treasury movement;
- `expense_paid` means the expense is fully settled, not that a new cash movement occurred.
"""
from decimal import Decimal

from django.dispatch import receiver

from django_expenses.signals import expense_approved, expense_payment_recorded


@receiver(expense_approved)
def on_expense_approved(sender, expense, user, **kwargs):
    """Connect this to the host project's OHADA accounting adapter.

    The exact payable/charge posting depends on whether the host runs cash-basis
    or accrual accounting, so django-expenses deliberately does not hard-code it.
    """
    charge_code = expense.suggested_account_code or "658"
    # Example host call:
    # AccountingAdapter.comptabiliser_depense_approuvee(
    #     reference=expense.reference_number,
    #     compte_charge=charge_code,
    #     montant=expense.total_amount,
    #     user=user,
    # )
    return charge_code


@receiver(expense_payment_recorded)
def on_expense_payment_recorded(sender, expense, payment, user, **kwargs):
    """Create one treasury movement per real payment, including partial payments."""
    from comptes.services.mouvement_service import MouvementService

    MouvementService.creer_mouvement(
        compte=None,  # Resolve payment.compte_reference in the host application.
        nature="DECAISSEMENT",
        montant=Decimal(str(payment.amount_paid)),
        libelle=f"Paiement dépense: {expense.reference_number}",
        date_mouvement=payment.payment_date,
        user=user,
    )
