from django.core.exceptions import PermissionDenied


class WorkflowError(Exception):
    pass


class StateMachine:
    TRANSITIONS = {
        "draft": ["submitted", "cancelled"],
        "submitted": ["pending_approval", "cancelled"],
        "pending_approval": ["approved", "rejected", "cancelled"],
        "approved": ["paid", "cancelled"],
        "rejected": ["submitted", "cancelled"],
        "paid": ["archived"],
        "archived": [],
        "cancelled": [],
    }

    @classmethod
    def is_allowed(cls, current_status, next_status):
        return next_status in cls.TRANSITIONS.get(current_status, [])

    @classmethod
    def assert_allowed(cls, current_status, next_status):
        if not cls.is_allowed(current_status, next_status):
            raise WorkflowError(
                f"Cannot transition from '{current_status}' to '{next_status}'."
            )

    @classmethod
    def next_statuses(cls, current_status):
        return cls.TRANSITIONS.get(current_status, [])

    @classmethod
    def requires_permission(cls, next_status):
        mapping = {
            "approved": "expenses.approve_expense",
            "paid": "expenses.pay_expense",
        }
        return mapping.get(next_status)
