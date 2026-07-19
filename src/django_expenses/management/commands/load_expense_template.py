from django.core.management.base import BaseCommand
from django.db import transaction

from ...models import ExpenseCategory
from ...constants import TEMPLATES as SOURCE_TEMPLATES


class Command(BaseCommand):
    help = "Load expense category template (default, ohada, ifrs, ngo)"

    def add_arguments(self, parser):
        parser.add_argument(
            "template",
            nargs="?",
            default="default",
            choices=list(SOURCE_TEMPLATES.keys()) + ["list"],
            help="Template name to load",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Delete existing categories before loading",
        )

    def handle(self, *args, **options):
        template_name = options["template"]

        if template_name == "list":
            self.stdout.write("Available templates:")
            for name, tpl in SOURCE_TEMPLATES.items():
                self.stdout.write(f"  {name}: {tpl['label']}")
                self.stdout.write(f"    {tpl['description']}")
            return

        template = SOURCE_TEMPLATES[template_name]

        if options["force"]:
            deleted, _ = ExpenseCategory.objects.all().delete()
            self.stdout.write(f"Deleted {deleted} existing categories.")

        created = 0
        parent_cache = {}

        fields = [
            "code", "name", "parent_code", "expense_nature",
            "default_account_code", "default_vat_rate",
            "requires_approval", "requires_receipt", "requires_vendor",
            "unit", "icon", "sort_order", "depreciation_rate",
        ]

        for entry in template["categories"]:
            data = dict(zip(fields, entry))
            code = data["code"]

            if ExpenseCategory.objects.filter(code=code).exists():
                self.stdout.write(f"  SKIP {code} (already exists)")
                continue

            parent = None
            if data["parent_code"]:
                parent = parent_cache.get(data["parent_code"])
                if not parent:
                    try:
                        parent = ExpenseCategory.objects.get(code=data["parent_code"])
                    except ExpenseCategory.DoesNotExist:
                        continue

            cat = ExpenseCategory.objects.create(
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
            parent_cache[code] = cat
            created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\nLoaded template '{template_name}': "
                f"{created} categories created."
            )
        )
