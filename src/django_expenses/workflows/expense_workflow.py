from ..constants import ExpenseStatus
from ..exceptions import WorkflowError
from ..permissions import APPROVE_EXPENSE, PAY_EXPENSE


class ExpenseWorkflow:
    TRANSITIONS = {
        ExpenseStatus.DRAFT: [ExpenseStatus.SUBMITTED, ExpenseStatus.CANCELLED],
        ExpenseStatus.SUBMITTED: [
            ExpenseStatus.PENDING_APPROVAL,
            ExpenseStatus.CANCELLED,
        ],
        ExpenseStatus.PENDING_APPROVAL: [
            ExpenseStatus.APPROVED,
            ExpenseStatus.REJECTED,
            ExpenseStatus.CANCELLED,
        ],
        ExpenseStatus.APPROVED: [ExpenseStatus.PAID, ExpenseStatus.CANCELLED],
        ExpenseStatus.REJECTED: [ExpenseStatus.SUBMITTED, ExpenseStatus.CANCELLED],
        ExpenseStatus.PAID: [ExpenseStatus.ARCHIVED],
        ExpenseStatus.ARCHIVED: [],
        ExpenseStatus.CANCELLED: [],
    }

    PERMISSION_MAP = {
        ExpenseStatus.APPROVED: APPROVE_EXPENSE,
        ExpenseStatus.PAID: PAY_EXPENSE,
    }

    @classmethod
    def is_allowed(cls, current, target):
        return target in cls.TRANSITIONS.get(current, [])

    @classmethod
    def assert_allowed(cls, current, target):
        if not cls.is_allowed(current, target):
            raise WorkflowError(
                f"Cannot transition from '{current}' to '{target}'."
            )

    @classmethod
    def next_statuses(cls, current):
        return list(cls.TRANSITIONS.get(current, []))

    @classmethod
    def requires_permission(cls, target):
        return cls.PERMISSION_MAP.get(target)
