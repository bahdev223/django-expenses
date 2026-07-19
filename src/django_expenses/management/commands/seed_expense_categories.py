from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from ....models import ExpenseCategory
from ....constants import DEFAULT_EXPENSE_CATEGORIES


class Command(BaseCommand):
    help = "Seed default expense categories (hierarchical with account codes)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Delete existing categories before seeding",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["force"]:
            deleted, _ = ExpenseCategory.objects.all().delete()
            self.stdout.write(f"Deleted {deleted} existing categories.")

        created = 0
        parent_cache = {}

        for code, name, parent_code, nature, account, sort in DEFAULT_EXPENSE_CATEGORIES:
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
                        self.stdout.write(
                            self.style.WARNING(
                                f"  WARN {code}: parent {parent_code} not found, skipping"
                            )
                        )
                        continue

            category = ExpenseCategory.objects.create(
                code=code,
                name=name,
                parent=parent,
                expense_nature=nature,
                default_account_code=account,
                sort_order=sort,
            )
            parent_cache[code] = category
            created += 1
            path = category.get_full_path()
            self.stdout.write(f"  OK   {code} - {path}")

        self.stdout.write(
            self.style.SUCCESS(f"\nCreated {created} expense categories.")
        )
