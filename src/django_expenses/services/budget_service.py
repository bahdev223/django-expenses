from django.core.exceptions import ValidationError
from django.db.models import Q

from ..models import BudgetDepense
from ..settings import EXPENSES


class BudgetService:
    @staticmethod
    def budgets_applicables(depense):
        return BudgetDepense.objects.filter(
            actif=True,
            date_debut__lte=depense.date_incurred,
            date_fin__gte=depense.date_incurred,
        ).filter(
            Q(categorie__isnull=True) | Q(categorie=depense.category),
            Q(centre_cout__isnull=True) | Q(centre_cout=depense.cost_center),
        )

    @classmethod
    def verifier_depense(cls, depense):
        if not EXPENSES["ENFORCE_BUDGET"]:
            return
        for budget in cls.budgets_applicables(depense):
            if budget.bloquant and depense.total_amount > budget.montant_disponible:
                raise ValidationError(
                    f"Budget '{budget.nom}' insuffisant : disponible "
                    f"{budget.montant_disponible}, dépense {depense.total_amount}."
                )
