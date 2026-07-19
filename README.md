# django-expenses

A professional, reusable **Expense Engine** for Django — not just a CRUD.

## Quick start

```bash
pip install django-expenses
```

```python
INSTALLED_APPS = [
    ...
    "django_expenses",
]
```

```bash
python manage.py migrate
```

You now have a complete expense management system with workflow, API, admin, permissions, and signals.

## Features

- **8 models**: Expense, ExpenseCategory, ExpenseType, CostCenter, ExpenseAttachment, ExpenseApproval, ExpensePayment, ExpenseComment
- **Full workflow**: Draft → Submitted → Pending Approval → Approved → Paid → Archived (with reject/cancel)
- **ExpenseService**: Every business action goes through the service layer
- **DRF API**: Full REST API with transition endpoints
- **Admin**: Ready-to-use admin with filters, search, bulk actions, export
- **Permissions**: 6 granular permissions (add, change, delete, approve, pay, view_reports)
- **Signals**: 7 events emitted for loose coupling (expense_created, expense_approved, etc.)
- **Zero business logic**: No dependency on any specific industry

## Configuration

```python
EXPENSES = {
    "CURRENCY": "USD",
    "CURRENCY_SYMBOL": "$",
    "DECIMAL_PLACES": 2,
    "AUTO_REFERENCE_PREFIX": "EXP",
    "REQUIRE_APPROVAL": True,
    "MAX_ATTACHMENTS": 5,
    "ALLOWED_ATTACHMENT_TYPES": ["pdf", "jpg", "png"],
    "ENABLE_COMMENTS": True,
}
```

## Workflow

```
Brouillon → Soumise → En attente d'approbation → Approuvée → Payée → Archivée
                                                ↘ Rejetée → Soumise
Tous les statuts peuvent être annulés (sauf Payée/Archivée)
```

## Signals

```python
from django_expenses.signals import expense_approved

@receiver(expense_approved)
def on_expense_approved(sender, expense, user, **kwargs):
    create_accounting_entry(expense)
```

## API

```
/expenses/              [GET, POST]
/expenses/{id}/submit/  [POST]
/expenses/{id}/approve/ [POST]
/expenses/{id}/pay/     [POST]
```

## License

MIT
