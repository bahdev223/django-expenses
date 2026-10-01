from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("django_expenses", "0004_budget_projets"),
    ]

    operations = [
        migrations.AddField(
            model_name="expense",
            name="entreprise_source",
            field=models.CharField(blank=True, db_index=True, max_length=80),
        ),
        migrations.AddField(
            model_name="expense",
            name="entreprise_reference",
            field=models.CharField(blank=True, db_index=True, max_length=120),
        ),
        migrations.AddField(
            model_name="expense",
            name="entreprise_libelle",
            field=models.CharField(blank=True, max_length=240),
        ),
        migrations.AddField(
            model_name="expensecategory",
            name="entreprise_source",
            field=models.CharField(blank=True, db_index=True, max_length=80),
        ),
        migrations.AddField(
            model_name="expensecategory",
            name="entreprise_reference",
            field=models.CharField(blank=True, db_index=True, max_length=120),
        ),
        migrations.AddField(
            model_name="expensecategory",
            name="entreprise_libelle",
            field=models.CharField(blank=True, max_length=240),
        ),
        migrations.AlterField(
            model_name="expensecategory",
            name="code",
            field=models.CharField(db_index=True, max_length=50),
        ),
        migrations.AddField(
            model_name="costcenter",
            name="entreprise_source",
            field=models.CharField(blank=True, db_index=True, max_length=80),
        ),
        migrations.AddField(
            model_name="costcenter",
            name="entreprise_reference",
            field=models.CharField(blank=True, db_index=True, max_length=120),
        ),
        migrations.AddField(
            model_name="costcenter",
            name="entreprise_libelle",
            field=models.CharField(blank=True, max_length=240),
        ),
        migrations.AlterField(
            model_name="costcenter",
            name="code",
            field=models.CharField(db_index=True, max_length=50),
        ),
        migrations.AddField(
            model_name="budgetdepense",
            name="entreprise_source",
            field=models.CharField(blank=True, db_index=True, max_length=80),
        ),
        migrations.AddField(
            model_name="budgetdepense",
            name="entreprise_reference",
            field=models.CharField(blank=True, db_index=True, max_length=120),
        ),
        migrations.AddField(
            model_name="budgetdepense",
            name="entreprise_libelle",
            field=models.CharField(blank=True, max_length=240),
        ),
        migrations.AddField(
            model_name="avancedepense",
            name="entreprise_source",
            field=models.CharField(blank=True, db_index=True, max_length=80),
        ),
        migrations.AddField(
            model_name="avancedepense",
            name="entreprise_reference",
            field=models.CharField(blank=True, db_index=True, max_length=120),
        ),
        migrations.AddField(
            model_name="avancedepense",
            name="entreprise_libelle",
            field=models.CharField(blank=True, max_length=240),
        ),
        migrations.AlterField(
            model_name="avancedepense",
            name="reference",
            field=models.CharField(db_index=True, max_length=100),
        ),
        migrations.AddField(
            model_name="evenementdepense",
            name="entreprise_source",
            field=models.CharField(blank=True, db_index=True, max_length=80),
        ),
        migrations.AddField(
            model_name="evenementdepense",
            name="entreprise_reference",
            field=models.CharField(blank=True, db_index=True, max_length=120),
        ),
        migrations.AddField(
            model_name="evenementdepense",
            name="entreprise_libelle",
            field=models.CharField(blank=True, max_length=240),
        ),
        migrations.AddConstraint(
            model_name="evenementdepense",
            constraint=models.CheckConstraint(
                check=(
                    models.Q(entreprise_source="", entreprise_reference="")
                    | (~models.Q(entreprise_source="") & ~models.Q(entreprise_reference=""))
                ),
                name="evenement_depense_entreprise_coherente",
            ),
        ),
        migrations.AddConstraint(
            model_name="expense",
            constraint=models.CheckConstraint(
                check=(
                    models.Q(entreprise_source="", entreprise_reference="")
                    | (~models.Q(entreprise_source="") & ~models.Q(entreprise_reference=""))
                ),
                name="expense_entreprise_coherente",
            ),
        ),
        migrations.AddConstraint(
            model_name="expensecategory",
            constraint=models.UniqueConstraint(
                fields=("entreprise_source", "entreprise_reference", "code"),
                name="expense_category_code_par_entreprise",
            ),
        ),
        migrations.AddConstraint(
            model_name="expensecategory",
            constraint=models.CheckConstraint(
                check=(
                    models.Q(entreprise_source="", entreprise_reference="")
                    | (~models.Q(entreprise_source="") & ~models.Q(entreprise_reference=""))
                ),
                name="expense_category_entreprise_coherente",
            ),
        ),
        migrations.AddConstraint(
            model_name="costcenter",
            constraint=models.UniqueConstraint(
                fields=("entreprise_source", "entreprise_reference", "code"),
                name="cost_center_code_par_entreprise",
            ),
        ),
        migrations.AddConstraint(
            model_name="costcenter",
            constraint=models.CheckConstraint(
                check=(
                    models.Q(entreprise_source="", entreprise_reference="")
                    | (~models.Q(entreprise_source="") & ~models.Q(entreprise_reference=""))
                ),
                name="cost_center_entreprise_coherente",
            ),
        ),
        migrations.AddConstraint(
            model_name="budgetdepense",
            constraint=models.CheckConstraint(
                check=(
                    models.Q(entreprise_source="", entreprise_reference="")
                    | (~models.Q(entreprise_source="") & ~models.Q(entreprise_reference=""))
                ),
                name="budget_depense_entreprise_coherente",
            ),
        ),
        migrations.AddConstraint(
            model_name="avancedepense",
            constraint=models.UniqueConstraint(
                fields=("entreprise_source", "entreprise_reference", "reference"),
                name="avance_reference_par_entreprise",
            ),
        ),
        migrations.AddConstraint(
            model_name="avancedepense",
            constraint=models.CheckConstraint(
                check=(
                    models.Q(entreprise_source="", entreprise_reference="")
                    | (~models.Q(entreprise_source="") & ~models.Q(entreprise_reference=""))
                ),
                name="avance_entreprise_coherente",
            ),
        ),
    ]
