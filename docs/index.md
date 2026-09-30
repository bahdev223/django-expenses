# django-expenses documentation

## Installation

```bash
pip install django-expenses
```

For the REST API:

```bash
pip install "django-expenses[api]"
```

Add the package to `INSTALLED_APPS` and run migrations:

```python
INSTALLED_APPS = [
    ...,
    "django_expenses",
]
```

```bash
python manage.py migrate
```

## French-first integration

Historical English imports remain available, but new projects can use the French facade:

```python
from django_expenses.models import Depense, CategorieDepense
from django_expenses.services import ServiceDepense

categorie = CategorieDepense.objects.get(code="FONCT_CARBURANT")

depense = ServiceDepense.creer(
    {
        "user": request.user,
        "category": categorie,
        "amount": 50_000,
        "description": "Carburant pour chantier",
        "vendor": "Station",
        "date_incurred": "2026-09-30",
    },
    user=request.user,
)
```

The compatibility facade intentionally does not rename database columns in place. This avoids breaking existing migrations and third-party integrations.

## Workflow

```text
Brouillon → Soumise → En attente → Approuvée
                               ↘ Rejetée
Approuvée → Partiellement payée → Payée → Archivée
```

Use `ExpenseService` / `ServiceDepense` for all business transitions. Do not update `status` directly.

## Payments

Payments support partial settlement, overpayment protection, idempotency and an external treasury account reference:

```python
ServiceDepense.payer(
    depense,
    user=request.user,
    payment_data={
        "amount_paid": 10_000,
        "payment_method": "cash",
        "compte_reference": "CAISSE-01",
        "cle_idempotence": "PAY-0001",
    },
)
```

## Budgets and advances

- `BudgetDepense` controls spending by period/category/cost center.
- `AvanceDepense` records an advance granted to a beneficiary.
- `JustificationAvance` records how the advance was used.
- Actual cash balances remain in the treasury engine (`django-comptes` or another host adapter).

## Audit

Every service-level operation creates an `EvenementDepense`. Draft deletion is logical rather than destructive.

## Integration signals

Use `expense_approved` for accounting recognition when appropriate and `expense_payment_recorded` for each real cash/bank/mobile-money movement. The latter is emitted once for every payment, including partial payments.

## Full reference

See the project README and source-level docstrings for configuration and extension hooks.
