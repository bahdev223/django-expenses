class ExpenseHook:
    """
    Base hook class for extending django-expenses behavior.
    Subclass and override methods to add custom logic at key points.
    """

    def before_create(self, data, user):
        """Called before an expense is created. Return modified data or raise."""

    def after_create(self, expense, user):
        """Called after an expense is created."""

    def before_transition(self, expense, target_status, user):
        """Called before a workflow transition. Raise to block."""

    def after_transition(self, expense, previous_status, user):
        """Called after a workflow transition."""

    def before_pay(self, expense, payment_data, user):
        """Called before payment is recorded. Return modified payment_data or raise."""

    def after_pay(self, expense, payment, user):
        """Called after payment is recorded."""


class HookRegistry:
    _hooks = []

    @classmethod
    def register(cls, hook):
        if hook not in cls._hooks:
            cls._hooks.append(hook)

    @classmethod
    def unregister(cls, hook):
        if hook in cls._hooks:
            cls._hooks.remove(hook)

    @classmethod
    def get_hooks(cls):
        return list(cls._hooks)
