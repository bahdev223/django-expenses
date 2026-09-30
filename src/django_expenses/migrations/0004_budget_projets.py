from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("django_expenses", "0003_stabilisation_v02"),
    ]

    operations = [
        migrations.AddField(
            model_name="expense",
            name="projet_source",
            field=models.CharField(
                blank=True,
                help_text="Application/source owning the project, e.g. solarplus or django_projets",
                max_length=80,
            ),
        ),
        migrations.AddField(
            model_name="expense",
            name="projet_reference",
            field=models.CharField(
                blank=True,
                db_index=True,
                help_text="Stable external project reference",
                max_length=120,
            ),
        ),
        migrations.AddField(
            model_name="expense",
            name="projet_libelle",
            field=models.CharField(
                blank=True,
                help_text="Project label snapshot for display",
                max_length=240,
            ),
        ),
        migrations.AddField(
            model_name="budgetdepense",
            name="projet_source",
            field=models.CharField(
                blank=True,
                help_text="Application/source owning the project",
                max_length=80,
            ),
        ),
        migrations.AddField(
            model_name="budgetdepense",
            name="projet_reference",
            field=models.CharField(
                blank=True,
                db_index=True,
                help_text="Stable external project reference",
                max_length=120,
            ),
        ),
        migrations.AddField(
            model_name="budgetdepense",
            name="projet_libelle",
            field=models.CharField(
                blank=True,
                help_text="Project label snapshot for display",
                max_length=240,
            ),
        ),
        migrations.AddConstraint(
            model_name="budgetdepense",
            constraint=models.CheckConstraint(
                check=(
                    models.Q(projet_source="", projet_reference="")
                    | (~models.Q(projet_source="") & ~models.Q(projet_reference=""))
                ),
                name="budget_depense_projet_coherent",
            ),
        ),
    ]
