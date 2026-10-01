from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from ...models import (
    AvanceDepense,
    BudgetDepense,
    CostCenter,
    EvenementDepense,
    Expense,
    ExpenseCategory,
)


class Command(BaseCommand):
    help = (
        "Rattache les données historiques sans entreprise à une entreprise. "
        "Les catégories restent globales par défaut."
    )

    def add_arguments(self, parser):
        parser.add_argument("--source", required=True)
        parser.add_argument("--reference", required=True)
        parser.add_argument("--libelle", default="")
        parser.add_argument(
            "--categories",
            action="store_true",
            help="Rattacher aussi les catégories actuellement globales.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        source = options["source"].strip()
        reference = options["reference"].strip()
        libelle = options["libelle"].strip()

        if not source or not reference:
            raise CommandError("--source et --reference sont obligatoires.")

        valeurs = {
            "entreprise_source": source,
            "entreprise_reference": reference,
            "entreprise_libelle": libelle,
        }

        resultats = {}
        for nom, modele in [
            ("depenses", Expense),
            ("centres_cout", CostCenter),
            ("budgets", BudgetDepense),
            ("avances", AvanceDepense),
            ("evenements", EvenementDepense),
        ]:
            resultats[nom] = modele.objects.filter(
                entreprise_source="",
                entreprise_reference="",
            ).update(**valeurs)

        if options["categories"]:
            resultats["categories"] = ExpenseCategory.objects.filter(
                entreprise_source="",
                entreprise_reference="",
            ).update(**valeurs)
        else:
            resultats["categories"] = 0

        self.stdout.write(self.style.SUCCESS("Rattachement terminé :"))
        for nom, total in resultats.items():
            self.stdout.write(f"  {nom}: {total}")
        if not options["categories"]:
            self.stdout.write(
                "  catégories globales conservées (utiliser --categories pour les rattacher)."
            )
