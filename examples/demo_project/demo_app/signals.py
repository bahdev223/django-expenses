"""
Example: Connect django-expenses signals to accounting.
"""
from django.dispatch import receiver
from django_expenses.signals import expense_approved, expense_paid


@receiver(expense_approved)
def on_expense_approved(sender, expense, user, **kwargs):
    print(f"[ACCOUNTING] Expense {expense.reference_number} approved: "
          f"{expense.total_amount} {expense.currency}")
    # In production: create OHADA journal entry here


@receiver(expense_paid)
def on_expense_paid(sender, expense, user, **kwargs):
    print(f"[TREASURY] Expense {expense.reference_number} paid: "
          f"{expense.total_amount} {expense.currency}")
    # In production: update cash/bank balance here
