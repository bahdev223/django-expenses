class ExpenseHook:
    """Base hook class for extending django-expenses behavior."""

    def before_create(self, data, user):
        return data

    def after_create(self, expense, user):
        pass

    def before_transition(self, expense, target_status, user):
        pass

    def after_transition(self, expense, previous_status, user):
        pass

    def before_pay(self, expense, payment_data, user):
        return payment_data

    def after_pay(self, expense, payment, user):
        pass

    def filter_queryset(self, queryset, user=None, request=None):
        """Allow the host project to enforce organisation/tenant scoping."""
        return queryset


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

    @classmethod
    def filter_queryset(cls, queryset, user=None, request=None):
        qs = queryset
        for hook in cls.get_hooks():
            qs = hook.filter_queryset(qs, user=user, request=request) or qs
        return qs
