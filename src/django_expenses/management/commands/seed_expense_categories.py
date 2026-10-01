from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from ...models import ExpenseCategory
from ...constants import DEFAULT_EXPENSE_CATEGORIES


class Command(BaseCommand):
    help = "Seed default expense categories (hierarchical with account codes)"

    def add_arguments(self, parser):
        parser.add_argument("--entreprise-source", default="")
        parser.add_argument("--entreprise-reference", default="")
        parser.add_argument("--entreprise-libelle", default="")
        parser.add_argument(
            "--force",
            action="store_true",
            help="Delete existing categories before seeding",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        source = options["entreprise_source"]
        reference = options["entreprise_reference"]
        libelle = options["entreprise_libelle"]
        if bool(source) != bool(reference):
            raise CommandError(
                "--entreprise-source et --entreprise-reference doivent être fournis ensemble."
            )
        scope = {
            "entreprise_source": source,
            "entreprise_reference": reference,
        }

        if options["force"]:
            deleted, _ = ExpenseCategory.objects.filter(**scope).delete()
            self.stdout.write(f"Deleted {deleted} existing categories.")

        created = 0
        parent_cache = {}

        fields = [
            "code", "name", "parent_code", "expense_nature",
            "default_account_code", "default_vat_rate",
            "requires_approval", "requires_receipt", "requires_vendor",
            "unit", "icon", "sort_order", "depreciation_rate",
        ]

        for entry in DEFAULT_EXPENSE_CATEGORIES:
            data = dict(zip(fields, entry))
            code = data["code"]

            if ExpenseCategory.objects.filter(code=code, **scope).exists():
                self.stdout.write(f"  SKIP {code} (already exists)")
                continue

            parent = None
            if data["parent_code"]:
                parent = parent_cache.get(data["parent_code"])
                if not parent:
                    try:
                        parent = ExpenseCategory.objects.get(
                            code=data["parent_code"],
                            **scope,
                        )
                    except ExpenseCategory.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(
                                f"  WARN {code}: parent {data['parent_code']} not found, skipping"
                            )
                        )
                        continue

            category = ExpenseCategory.objects.create(
                entreprise_source=source,
                entreprise_reference=reference,
                entreprise_libelle=libelle,
                code=code,
                name=data["name"],
                parent=parent,
                expense_nature=data["expense_nature"] or "",
                default_account_code=data["default_account_code"] or "",
                default_vat_rate=data["default_vat_rate"] or 0,
                requires_approval=data["requires_approval"],
                requires_receipt=data["requires_receipt"],
                requires_vendor=data["requires_vendor"],
                unit=data["unit"] or "",
                icon=data["icon"] or "",
                sort_order=data["sort_order"] or 0,
                depreciation_rate=data["depreciation_rate"],
            )
            parent_cache[code] = category
            created += 1
            self.stdout.write(f"  OK   {code} - {category.get_full_path()}")

        self.stdout.write(
            self.style.SUCCESS(f"\nCreated {created} expense categories.")
        )
