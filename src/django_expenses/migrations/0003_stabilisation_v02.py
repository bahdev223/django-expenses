from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def migrer_natures_francaises(apps, schema_editor):
    Expense = apps.get_model("django_expenses", "Expense")
    ExpenseCategory = apps.get_model("django_expenses", "ExpenseCategory")
    correspondances = {
        "operating": "fonctionnement",
        "investment": "investissement",
        "mission": "fonctionnement",
        "purchase": "achat",
        "payroll": "personnel",
        "other": "divers",
    }
    for ancien, nouveau in correspondances.items():
        Expense.objects.filter(expense_nature=ancien).update(expense_nature=nouveau)
        ExpenseCategory.objects.filter(expense_nature=ancien).update(expense_nature=nouveau)


def retour_natures_anglais(apps, schema_editor):
    Expense = apps.get_model("django_expenses", "Expense")
    ExpenseCategory = apps.get_model("django_expenses", "ExpenseCategory")
    correspondances = {
        "fonctionnement": "operating",
        "investissement": "investment",
        "achat": "purchase",
        "personnel": "payroll",
        "divers": "other",
    }
    for nouveau, ancien in correspondances.items():
        Expense.objects.filter(expense_nature=nouveau).update(expense_nature=ancien)
        ExpenseCategory.objects.filter(expense_nature=nouveau).update(expense_nature=ancien)


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("django_expenses", "0002_expensecategory_depreciation_rate_and_more"),
    ]

    operations = [
        migrations.RunPython(migrer_natures_francaises, retour_natures_anglais),
        migrations.AlterField(
            model_name="expense",
            name="status",
            field=models.CharField(
                choices=[
                    ("draft", "Brouillon"),
                    ("submitted", "Soumise"),
                    ("pending_approval", "En attente d'approbation"),
                    ("approved", "Approuvée"),
                    ("rejected", "Rejetée"),
                    ("partiellement_payee", "Partiellement payée"),
                    ("paid", "Payée"),
                    ("archived", "Archivée"),
                    ("cancelled", "Annulée"),
                ],
                db_index=True,
                default="draft",
                max_length=24,
            ),
        ),
        migrations.AlterField(
            model_name="expense",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="expenses",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="expense",
            name="supprime_le",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="expense",
            name="supprime_par",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="depenses_supprimees",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="expenseapproval",
            name="approved_by",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="expense_approvals",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="expenseapproval",
            name="expense",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="approvals",
                to="django_expenses.expense",
            ),
        ),
        migrations.AlterField(
            model_name="expensepayment",
            name="expense",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="payments",
                to="django_expenses.expense",
            ),
        ),
        migrations.AddField(
            model_name="expensepayment",
            name="cle_idempotence",
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="expensepayment",
            name="compte_reference",
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AlterModelOptions(
            name="expensepayment",
            options={
                "ordering": ["-payment_date", "-created_at"],
                "verbose_name": "Expense payment",
                "verbose_name_plural": "Expense payments",
            },
        ),
        migrations.AddConstraint(
            model_name="expense",
            constraint=models.CheckConstraint(
                check=models.Q(("amount__gt", 0)),
                name="expense_amount_gt_zero",
            ),
        ),
        migrations.AddConstraint(
            model_name="expense",
            constraint=models.CheckConstraint(
                check=models.Q(("tax_amount__gte", 0)),
                name="expense_tax_gte_zero",
            ),
        ),
        migrations.AddConstraint(
            model_name="expensepayment",
            constraint=models.CheckConstraint(
                check=models.Q(("amount_paid__gt", 0)),
                name="expense_payment_amount_gt_zero",
            ),
        ),
        migrations.CreateModel(
            name="BudgetDepense",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nom", models.CharField(max_length=200)),
                ("date_debut", models.DateField()),
                ("date_fin", models.DateField()),
                ("montant_alloue", models.DecimalField(decimal_places=2, max_digits=15)),
                ("bloquant", models.BooleanField(default=True)),
                ("actif", models.BooleanField(default=True)),
                ("cree_le", models.DateTimeField(auto_now_add=True)),
                ("modifie_le", models.DateTimeField(auto_now=True)),
                ("categorie", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="budgets_depenses", to="django_expenses.expensecategory")),
                ("centre_cout", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="budgets_depenses", to="django_expenses.costcenter")),
            ],
            options={
                "verbose_name": "Budget de dépense",
                "verbose_name_plural": "Budgets de dépenses",
                "ordering": ["-date_debut", "nom"],
            },
        ),
        migrations.AddConstraint(
            model_name="budgetdepense",
            constraint=models.CheckConstraint(
                check=models.Q(("montant_alloue__gte", 0)),
                name="budget_depense_montant_gte_zero",
            ),
        ),
        migrations.AddConstraint(
            model_name="budgetdepense",
            constraint=models.CheckConstraint(
                check=models.Q(date_fin__gte=models.F("date_debut")),
                name="budget_depense_dates_valides",
            ),
        ),
        migrations.CreateModel(
            name="AvanceDepense",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("montant_accorde", models.DecimalField(decimal_places=2, max_digits=15)),
                ("date_avance", models.DateField()),
                ("objet", models.CharField(max_length=300)),
                ("statut", models.CharField(choices=[("ouverte", "Ouverte"), ("partiellement_justifiee", "Partiellement justifiée"), ("justifiee", "Justifiée"), ("soldee", "Soldée"), ("annulee", "Annulée")], default="ouverte", max_length=30)),
                ("reference", models.CharField(max_length=100, unique=True)),
                ("compte_reference", models.CharField(blank=True, max_length=120)),
                ("notes", models.TextField(blank=True)),
                ("cree_le", models.DateTimeField(auto_now_add=True)),
                ("modifie_le", models.DateTimeField(auto_now=True)),
                ("beneficiaire", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="avances_depenses_recues", to=settings.AUTH_USER_MODEL)),
                ("cree_par", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="avances_depenses_creees", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Avance de dépense",
                "verbose_name_plural": "Avances de dépenses",
                "ordering": ["-date_avance", "-cree_le"],
            },
        ),
        migrations.AddConstraint(
            model_name="avancedepense",
            constraint=models.CheckConstraint(
                check=models.Q(("montant_accorde__gt", 0)),
                name="avance_depense_montant_gt_zero",
            ),
        ),
        migrations.CreateModel(
            name="JustificationAvance",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("montant", models.DecimalField(decimal_places=2, max_digits=15)),
                ("date_depense", models.DateField()),
                ("description", models.TextField()),
                ("piece", models.FileField(blank=True, upload_to="expenses/advance_receipts/%Y/%m/")),
                ("cree_le", models.DateTimeField(auto_now_add=True)),
                ("avance", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="justifications", to="django_expenses.avancedepense")),
                ("depense", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="justification_avance", to="django_expenses.expense")),
            ],
            options={
                "verbose_name": "Justification d'avance",
                "verbose_name_plural": "Justifications d'avances",
                "ordering": ["date_depense", "cree_le"],
            },
        ),
        migrations.AddConstraint(
            model_name="justificationavance",
            constraint=models.CheckConstraint(
                check=models.Q(("montant__gt", 0)),
                name="justification_avance_montant_gt_zero",
            ),
        ),
        migrations.CreateModel(
            name="EvenementDepense",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("reference_depense", models.CharField(db_index=True, max_length=100)),
                ("action", models.CharField(db_index=True, max_length=80)),
                ("donnees", models.JSONField(blank=True, default=dict)),
                ("cree_le", models.DateTimeField(auto_now_add=True)),
                ("acteur", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="evenements_depenses", to=settings.AUTH_USER_MODEL)),
                ("depense", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="evenements", to="django_expenses.expense")),
            ],
            options={
                "verbose_name": "Événement de dépense",
                "verbose_name_plural": "Événements de dépenses",
                "ordering": ["-cree_le", "-id"],
            },
        ),
    ]
