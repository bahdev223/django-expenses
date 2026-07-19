# django-expenses documentation

## Installation

```bash
pip install django-expenses
```

Add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    "django_expenses",
]
```

Run migrations:

```bash
python manage.py migrate
```

## Quick start

```python
from django_expenses.services import ExpenseService

# Create
expense = ExpenseService.create({
    "user": request.user,
    "expense_type": expense_type,
    "amount": 50000,
    "description": "Carburant pour chantier",
    "vendor": "Station Total",
    "date_incurred": "2026-07-01",
})

# Submit
ExpenseService.submit(expense)

# Approve (requires approve_expense permission)
ExpenseService.approve(expense, user=approver, comment="OK")

# Pay (requires pay_expense permission)
ExpenseService.pay(expense, user=admin, payment_data={"payment_method": "cash"})
```

## Full documentation

See [ReadTheDocs](https://django-expenses.readthedocs.io/).
