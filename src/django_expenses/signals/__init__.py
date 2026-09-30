from django.dispatch import Signal

expense_created = Signal()
expense_updated = Signal()
expense_submitted = Signal()
expense_approved = Signal()
expense_rejected = Signal()
expense_payment_recorded = Signal()
expense_paid = Signal()
expense_cancelled = Signal()
expense_deleted = Signal()

avance_creee = Signal()
avance_justifiee = Signal()
avance_soldee = Signal()
