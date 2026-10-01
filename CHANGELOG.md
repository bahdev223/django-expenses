# Changelog

## Unreleased - Multi-entreprise

- Isolation stricte par `entreprise_source + entreprise_reference`
- Resolver serveur pour le contexte entreprise, avec refus par défaut si absent
- Dépenses, budgets, avances, centres de coût et audit scindés par entreprise
- Catégories globales partageables et catégories propres à chaque entreprise
- Codes catégories/centres de coût/références d'avance uniques par entreprise
- API, rapports et Django Admin scindés par entreprise
- Migration `0005_multi_entreprise`
- Commande `assign_legacy_entreprise` pour rattacher les anciennes données
- Seed/templates de catégories sécurisés par entreprise
- Tests d'isolation inter-entreprises


## 0.2.0 (2026-09-30)

### Financial correctness

- Added partial-payment status and cumulative payment tracking.
- Added overpayment and non-positive payment protection.
- Added payment idempotency keys.
- Added external treasury account references (`compte_reference`).
- Added blocking expense budgets.
- Added advances and advance justifications.
- Added immutable expense event audit records.
- Replaced destructive draft deletion with logical deletion.
- Protected historical financial records from user/approval/payment cascades.

### Security and workflow

- Fixed permission namespace from `expenses.*` to the real `django_expenses.*` app label.
- Added permission enforcement to service transitions.
- Routed built-in API create/update/delete operations through `ExpenseService`.
- Routed built-in HTML create/update/delete operations through `ExpenseService`.
- Restricted admin mutations for payments, approvals and audit events.
- Added host-level queryset scoping hook for multi-tenant integrations.

### Reliability

- Fixed report status lookup (`Expense.Status` → `ExpenseStatus.CHOICES`).
- Fixed admin CSV export (`ExpenseService.export_csv` → `ReportService.export_csv`).
- Removed duplicate business-signal emission from model save receivers.
- Reference generation now respects `AUTO_REFERENCE_PREFIX`.
- Attachment count/type, vendor and receipt requirements are enforced.
- Added DB constraints for positive expense/payment/advance amounts and non-negative taxes.
- Added a data migration for historical English expense-nature values.

### Compatibility and naming

- Kept all historical English model names and API fields compatible.
- Added French aliases: `Depense`, `CategorieDepense`, `CentreCout`, `PaiementDepense`, `ApprobationDepense`, etc.
- Added `ServiceDepense` as the French service facade for new integrations.
- Corrected documentation: v0.1 contained 7 actual models, not the previously documented 8 (`ExpenseType` never existed).

## 0.1.0 (2026-07-19)

- Initial release.
- 7 actual models: Expense, ExpenseCategory, CostCenter, ExpenseAttachment, ExpenseApproval, ExpensePayment, ExpenseComment.
- Workflow engine (Draft → Submitted → Pending Approval → Approved → Paid → Archived).
- ExpenseService, DRF API, admin, permissions, signals and reference generation.
