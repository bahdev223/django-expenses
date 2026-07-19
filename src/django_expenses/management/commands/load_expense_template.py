from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from ....models import ExpenseCategory
from ....constants import DEFAULT_EXPENSE_CATEGORIES


TEMPLATES = {
    "default": {
        "label": "Default categories",
        "description": "Standard categories for any organization",
        "categories": DEFAULT_EXPENSE_CATEGORIES,
    },
}


class Command(BaseCommand):
    help = "Load expense category template (default, ohada, ifrs, ngo)"

    def add_arguments(self, parser):
        parser.add_argument(
            "template",
            nargs="?",
            default="default",
            choices=list(TEMPLATES.keys()) + ["list"],
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
            for name, tpl in TEMPLATES.items():
                self.stdout.write(f"  {name}: {tpl['label']}")
                self.stdout.write(f"    {tpl['description']}")
            return

        template = TEMPLATES[template_name]

        if options["force"]:
            deleted, _ = ExpenseCategory.objects.all().delete()
            self.stdout.write(f"Deleted {deleted} existing categories.")

        created = 0
        parent_cache = {}

        for code, name, parent_code, nature, account, sort in template["categories"]:
            if ExpenseCategory.objects.filter(code=code).exists():
                self.stdout.write(f"  SKIP {code} (already exists)")
                continue

            parent = None
            if parent_code:
                parent = parent_cache.get(parent_code)
                if not parent:
                    try:
                        parent = ExpenseCategory.objects.get(code=parent_code)
                    except ExpenseCategory.DoesNotExist:
                        continue

            cat = ExpenseCategory.objects.create(
                code=code,
                name=name,
                parent=parent,
                expense_nature=nature,
                default_account_code=account,
                sort_order=sort,
            )
            parent_cache[code] = cat
            created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\nLoaded template '{template_name}': "
                f"{created} categories created."
            )
        )
