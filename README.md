# django-expenses

A reusable **expense-management engine for Django** with workflow, approvals, partial payments, budgets, advances, audit history, DRF API and integration hooks.

Version **0.2** stabilizes the financial core and keeps backward compatibility with the historical English API while exposing a French domain facade for new SahelTech projects.

## Quick start

```bash
pip install django-expenses
```

```python
INSTALLED_APPS = [
    ...,
    "django_expenses",
]
```

```bash
python manage.py migrate
```

Install the optional REST API dependencies with:

```bash
pip install "django-expenses[api]"
```

## Domain model

The package now contains 11 models:

- `Expense` / `Depense`
- `ExpenseCategory` / `CategorieDepense`
- `CostCenter` / `CentreCout`
- `ExpenseAttachment` / `PieceJointeDepense`
- `ExpenseApproval` / `ApprobationDepense`
- `ExpensePayment` / `PaiementDepense`
- `ExpenseComment` / `CommentaireDepense`
- `BudgetDepense`
- `AvanceDepense`
- `JustificationAvance`
- `EvenementDepense`

The historical English names remain supported. New domain concepts and public aliases are French-first.

## Workflow

```text
Brouillon
  → Soumise
    → En attente d'approbation
      → Approuvée
        → Partiellement payée
          → Payée
            → Archivée
      ↘ Rejetée → Soumise
```

Cancellation is allowed only before money has moved. A partially or fully paid expense cannot be cancelled through the normal workflow.

## Partial payments

`ExpensePayment` is now a real multi-payment ledger. An expense is marked `Payée` only when the cumulative payments cover the exact total.

```python
from django_expenses.services import ServiceDepense

ServiceDepense.payer(
    depense,
    user=request.user,
    payment_data={
        "amount_paid": 10000,
        "payment_method": "cash",
        "compte_reference": "CAISSE-PRINCIPALE",
        "cle_idempotence": "PAY-2026-0001",
    },
)
```

Overpayment, negative payment amounts and duplicate idempotency keys are rejected.

## Budgets

`BudgetDepense` can target a category, a cost center, both, or neither. A blocking active budget is checked before approval.

```python
from django_expenses.models import BudgetDepense

BudgetDepense.objects.create(
    nom="Fonctionnement octobre",
    date_debut="2026-10-01",
    date_fin="2026-10-31",
    montant_alloue=2_000_000,
    bloquant=True,
)
```

## Advances / petty-cash workflow

`AvanceDepense` and `JustificationAvance` manage employee advances and their supporting expenses without duplicating cash balances.

The actual cash/bank/mobile-money balance remains the responsibility of a treasury engine such as `django-comptes`. Use `compte_reference` to link the advance or payment to that external account.

```python
from django_expenses.services import AvanceService

avance = AvanceService.creer(
    beneficiaire=employe,
    montant_accorde=50_000,
    date_avance="2026-10-01",
    objet="Mission terrain",
    reference="AV-2026-001",
    cree_par=request.user,
    compte_reference="CAISSE-01",
)
```

## Audit

Every service-level business action writes an immutable `EvenementDepense` record. Deleting a draft through `ExpenseService.delete()` is a **logical deletion**: the financial record is preserved and marked cancelled instead of being physically removed.

## Configuration

```python
EXPENSES = {
    "CURRENCY": "XOF",
    "CURRENCY_SYMBOL": "CFA",
    "DECIMAL_PLACES": 0,
    "AUTO_REFERENCE_PREFIX": "DEP",
    "REQUIRE_APPROVAL": True,
    "MAX_ATTACHMENTS": 5,
    "ALLOWED_ATTACHMENT_TYPES": ["pdf", "jpg", "jpeg", "png"],
    "ENABLE_COMMENTS": True,
    "ENABLE_WORKFLOW": True,
    "ALLOW_PARTIAL_PAYMENTS": True,
    "REQUIRE_ACCOUNT_REFERENCE": False,
    "ENFORCE_BUDGET": True,
}
```

## Permissions

The Django app label is intentionally kept as `django_expenses` for migration and content-type compatibility.

```text
django_expenses.add_expense
django_expenses.change_expense
django_expenses.delete_expense
django_expenses.view_expense
django_expenses.approve_expense
django_expenses.pay_expense
django_expenses.view_expense_reports
```

Do not rename the app label to `expenses` in an existing installation.

## Signals

Business signals are emitted by the service layer only, avoiding duplicate accounting or treasury side effects.

```python
from django.dispatch import receiver
from django_expenses.signals import expense_payment_recorded

@receiver(expense_payment_recorded)
def on_payment(sender, expense, payment, user, **kwargs):
    # Create exactly one treasury movement for this payment.
    pass
```

Important signals include `expense_created`, `expense_updated`, `expense_submitted`, `expense_approved`, `expense_rejected`, `expense_payment_recorded`, `expense_paid`, `expense_cancelled` and `expense_deleted`.

## Tenant / organisation scoping

The package remains industry- and tenant-agnostic. Host applications can register an `ExpenseHook.filter_queryset()` implementation to enforce organisation-level filtering consistently in the built-in API and HTML views.

## API

With `django-expenses[api]` installed:

```text
/api/expenses/
/api/expenses/{id}/submit/
/api/expenses/{id}/request_approval/
/api/expenses/{id}/approve/
/api/expenses/{id}/reject/
/api/expenses/{id}/pay/
/api/expenses/{id}/attachment/
/api/expenses/report/
/api/expenses/export/
/api/budgets/
/api/advances/
/api/advances/{id}/justifier/
/api/advances/{id}/solder/
```

## Category templates

The repository ships `default`, `ohada` and `light` category templates. The default/OHADA dataset contains roughly 188 predefined categories with account suggestions, VAT rates, approval/receipt requirements and units.

```bash
python manage.py load_expense_template ohada
```

## License

MIT


## Multi-entreprise

Le moteur peut fonctionner en mono-entreprise (comportement historique) ou en
multi-entreprise strict.

```python
EXPENSES = {
    "ENABLE_MULTI_ENTREPRISE": True,
    "ENTREPRISE_RESOLVER": "mon_projet.tenancy.resolve_expense_company",
    "ALLOW_GLOBAL_CATEGORIES": True,
}
```

Le resolver est exécuté côté serveur et doit retourner une entreprise déjà
autorisée pour l'utilisateur courant :

```python
def resolve_expense_company(request):
    organisation = request.organisation_active
    return {
        "source": "saheltech-platform",
        "reference": str(organisation.pk),
        "libelle": organisation.nom,
    }
```

Le client HTTP ne choisit jamais directement l'entreprise de la dépense. Les
champs `entreprise_source`, `entreprise_reference` et
`entreprise_libelle` sont injectés depuis ce contexte serveur.

Quand le mode multi-entreprise est actif sans contexte valide, les API et
l'admin refusent l'accès (fail-closed).

Les données sont isolées sur :

- dépenses ;
- budgets ;
- avances ;
- centres de coût ;
- catégories propres à l'entreprise ;
- paiements, approbations, commentaires et pièces jointes via leur dépense ;
- événements d'audit.

Les catégories OHADA peuvent rester globales et en lecture seule pour les
entreprises. Un même code de catégorie ou de centre de coût peut exister dans
plusieurs entreprises.

Avant d'activer le multi-entreprise sur une base existante :

```bash
python manage.py migrate
python manage.py assign_legacy_entreprise \
  --source saheltech-platform \
  --reference ENT-001 \
  --libelle "Entreprise démo"
```

Les catégories restent globales par défaut. Ajouter `--categories` uniquement
si les catégories historiques doivent devenir propres à cette entreprise.

## Budgets rattachés aux projets

Un budget peut rester global ou être limité à un projet externe sans dépendance forte
envers Solarplus ou un moteur de projets particulier.

```python
budget = BudgetDepense.objects.create(
    nom="Installation solaire - lot 2026",
    date_debut="2026-09-01",
    date_fin="2026-12-31",
    montant_alloue=5_000_000,
    projet_source="solarplus",
    projet_reference="PROJ-2026-0042",
    projet_libelle="Installation Sikasso",
)
```

Les dépenses du projet portent la même clé :

```python
depense = ExpenseService.create({
    "user": request.user,
    "category": categorie,
    "amount": 125_000,
    "description": "Transport matériel",
    "date_incurred": "2026-09-15",
    "projet_source": "solarplus",
    "projet_reference": "PROJ-2026-0042",
    "projet_libelle": "Installation Sikasso",
}, user=request.user)
```

Un budget avec `projet_reference` ne consomme et ne bloque que les dépenses portant
exactement le même couple `projet_source + projet_reference`. Les budgets sans projet
restent globaux et continuent à s'appliquer normalement.

