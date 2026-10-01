from django.core.exceptions import ValidationError
from django.db.models import Q

from ..models import BudgetDepense
from ..settings import EXPENSES


class BudgetService:
    @staticmethod
    def budgets_applicables(depense):
        qs = BudgetDepense.objects.filter(
            actif=True,
            entreprise_source=depense.entreprise_source,
            entreprise_reference=depense.entreprise_reference,
            date_debut__lte=depense.date_incurred,
            date_fin__gte=depense.date_incurred,
        ).filter(
            Q(categorie__isnull=True) | Q(categorie=depense.category),
            Q(centre_cout__isnull=True) | Q(centre_cout=depense.cost_center),
        )
        # Un budget sans projet reste global. Un budget projet ne s'applique
        # qu'aux dépenses portant exactement la même source/référence projet.
        return qs.filter(
            Q(projet_reference="")
            | Q(
                projet_source=depense.projet_source,
                projet_reference=depense.projet_reference,
            )
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
