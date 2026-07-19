from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="CostCenter",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=50, unique=True)),
                ("name", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("manager", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="managed_cost_centers", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Cost center",
                "verbose_name_plural": "Cost centers",
                "ordering": ["code"],
            },
        ),
        migrations.CreateModel(
            name="Expense",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[
                    ("draft", "Brouillon"), ("submitted", "Soumise"),
                    ("pending_approval", "En attente d'approbation"),
                    ("approved", "Approuv\u00e9e"), ("rejected", "Rejet\u00e9e"),
                    ("paid", "Pay\u00e9e"), ("archived", "Archiv\u00e9e"),
                    ("cancelled", "Annul\u00e9e"),
                ], db_index=True, default="draft", max_length=20)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=15)),
                ("tax_amount", models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ("currency", models.CharField(default="XOF", max_length=3)),
                ("description", models.TextField()),
                ("vendor", models.CharField(blank=True, max_length=300)),
                ("date_incurred", models.DateField()),
                ("date_submitted", models.DateTimeField(blank=True, null=True)),
                ("date_approved", models.DateTimeField(blank=True, null=True)),
                ("date_paid", models.DateTimeField(blank=True, null=True)),
                ("rejection_reason", models.TextField(blank=True)),
                ("payment_method", models.CharField(blank=True, choices=[
                    ("cash", "Esp\u00e8ces"), ("check", "Ch\u00e8que"),
                    ("bank_transfer", "Virement bancaire"),
                    ("mobile_money", "Mobile Money"), ("card", "Carte bancaire"),
                    ("other", "Autre"),
                ], max_length=20)),
                ("reference_number", models.CharField(blank=True, max_length=100, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Expense",
                "verbose_name_plural": "Expenses",
                "ordering": ["-created_at"],
                "permissions": [
                    ("approve_expense", "Can approve expenses"),
                    ("pay_expense", "Can mark expenses as paid"),
                    ("view_expense_reports", "Can view expense reports"),
                ],
            },
        ),
        migrations.CreateModel(
            name="ExpenseCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("sort_order", models.IntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Expense category",
                "verbose_name_plural": "Expense categories",
                "ordering": ["sort_order", "name"],
            },
        ),
        migrations.CreateModel(
            name="ExpenseType",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                ("requires_approval", models.BooleanField(default=True)),
                ("max_amount", models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("category", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="expense_types", to="django_expenses.expensecategory")),
            ],
            options={
                "verbose_name": "Expense type",
                "verbose_name_plural": "Expense types",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="ExpensePayment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("amount_paid", models.DecimalField(decimal_places=2, max_digits=15)),
                ("payment_date", models.DateField()),
                ("payment_method", models.CharField(blank=True, choices=[
                    ("cash", "Esp\u00e8ces"), ("check", "Ch\u00e8que"),
                    ("bank_transfer", "Virement bancaire"),
                    ("mobile_money", "Mobile Money"), ("card", "Carte bancaire"),
                    ("other", "Autre"),
                ], max_length=20)),
                ("reference", models.CharField(blank=True, max_length=200)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("expense", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="payments", to="django_expenses.expense")),
                ("paid_by", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="expense_payments", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Expense payment",
                "verbose_name_plural": "Expense payments",
                "ordering": ["-payment_date"],
            },
        ),
        migrations.CreateModel(
            name="ExpenseComment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("comment", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("expense", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="comments", to="django_expenses.expense")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="expense_comments", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Expense comment",
                "verbose_name_plural": "Expense comments",
                "ordering": ["created_at"],
            },
        ),
        migrations.CreateModel(
            name="ExpenseAttachment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("file", models.FileField(upload_to="expenses/attachments/%Y/%m/")),
                ("filename", models.CharField(max_length=500)),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                ("expense", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attachments", to="django_expenses.expense")),
            ],
            options={
                "verbose_name": "Expense attachment",
                "verbose_name_plural": "Expense attachments",
                "ordering": ["-uploaded_at"],
            },
        ),
        migrations.CreateModel(
            name="ExpenseApproval",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("decision", models.CharField(choices=[("approved", "Approuv\u00e9e"), ("rejected", "Rejet\u00e9e")], max_length=10)),
                ("comment", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("approved_by", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="expense_approvals", to=settings.AUTH_USER_MODEL)),
                ("expense", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="approvals", to="django_expenses.expense")),
            ],
            options={
                "verbose_name": "Expense approval",
                "verbose_name_plural": "Expense approvals",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddField(
            model_name="expense",
            name="approved_by",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="approved_expenses", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name="expense",
            name="cost_center",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="expenses", to="django_expenses.costcenter"),
        ),
        migrations.AddField(
            model_name="expense",
            name="expense_type",
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="expenses", to="django_expenses.expensetype"),
        ),
        migrations.AddField(
            model_name="expense",
            name="user",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="expenses", to=settings.AUTH_USER_MODEL),
        ),
    ]
