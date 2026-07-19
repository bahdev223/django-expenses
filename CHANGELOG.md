# Changelog

## 0.1.0 (2026-07-19)

- Initial release
- 8 models: Expense, ExpenseCategory, ExpenseType, CostCenter, ExpenseAttachment, ExpenseApproval, ExpensePayment, ExpenseComment
- Full workflow engine (Draft → Submitted → Pending Approval → Approved → Paid → Archived)
- ExpenseService with create, submit, approve, reject, pay, cancel, archive, export
- DRF API with transition endpoints
- Unfold-ready admin with filters, search, bulk actions
- 6 custom permissions
- 7 signals (expense_created, expense_updated, expense_submitted, expense_approved, expense_rejected, expense_paid, expense_cancelled)
- Auto-reference numbering
- Audit trail via ExpenseApproval
