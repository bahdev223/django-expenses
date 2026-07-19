"""
Example: Integrating django-expenses with Solar Plus ERP accounting.
This shows how to listen to expense signals and create OHADA accounting entries.
"""
from django.dispatch import receiver
from django_expenses.signals import expense_approved, expense_paid


@receiver(expense_approved)
def on_expense_approved(sender, expense, user, **kwargs):
    """When an expense is approved, create an accounting entry."""
    from comptabilite_ohada.services.ecriture_service import EcritureService
    svc = EcritureService()
    # Use the category's default account code, fallback to 658
    charge_code = expense.suggested_account_code or "658"
    svc.creer_ecriture_charge(
        compte_caisse_code="571",
        montant=float(expense.total_amount),
        libelle=f"Depense approuvee: {expense.reference_number} - {expense.description[:50]}",
        compte_charge_code=charge_code,
        user=user,
    )


@receiver(expense_paid)
def on_expense_paid(sender, expense, user, **kwargs):
    """When an expense is paid, update cash/bank balance."""
    from comptes.services.mouvement_service import MouvementService
    from decimal import Decimal
    MouvementService.creer_mouvement(
        compte=None,
        nature="DECAISSEMENT",
        montant=Decimal(str(expense.total_amount)),
        libelle=f"Paiement depense: {expense.reference_number}",
        date_mouvement=expense.date_paid.date() if expense.date_paid else expense.date_incurred,
        user=user,
    )


"""
To activate in your Django project's AppConfig.ready():

    from django_expenses.signals import expense_approved, expense_paid

Then connect the receivers above.
"""
