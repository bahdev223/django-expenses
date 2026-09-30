from rest_framework.permissions import BasePermission


class ActionDjangoModelPermissions(BasePermission):
    """Django model permissions aware of DRF ViewSet action names.

    DRF's stock DjangoModelPermissions maps every POST to `add_*`, including
    custom detail actions such as approve/pay. This class maps CRUD actions to
    their natural permission and lets each ViewSet override custom actions.
    """

    default_action_map = {
        "list": "view",
        "retrieve": "view",
        "create": "add",
        "update": "change",
        "partial_update": "change",
        "destroy": "delete",
    }

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        action = getattr(view, "action", None)
        explicit = getattr(view, "action_permission_map", {}).get(action)
        if explicit:
            return user.has_perm(explicit)

        prefix = self.default_action_map.get(action, "change")
        queryset = getattr(view, "queryset", None)
        if queryset is not None:
            model = queryset.model
        else:
            model = view.get_queryset().model
        permission = f"{model._meta.app_label}.{prefix}_{model._meta.model_name}"
        return user.has_perm(permission)
