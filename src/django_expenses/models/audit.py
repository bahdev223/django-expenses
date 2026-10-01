from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class EvenementDepense(models.Model):
    entreprise_source = models.CharField(max_length=80, blank=True, db_index=True)
    entreprise_reference = models.CharField(max_length=120, blank=True, db_index=True)
    entreprise_libelle = models.CharField(max_length=240, blank=True)
    depense = models.ForeignKey(
        "Expense",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="evenements",
    )
    reference_depense = models.CharField(max_length=100, db_index=True)
    action = models.CharField(max_length=80, db_index=True)
    acteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="evenements_depenses",
    )
    donnees = models.JSONField(default=dict, blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-cree_le", "-id"]
        verbose_name = _("Événement de dépense")
        verbose_name_plural = _("Événements de dépenses")
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(entreprise_source="", entreprise_reference="")
                    | (~models.Q(entreprise_source="") & ~models.Q(entreprise_reference=""))
                ),
                name="evenement_depense_entreprise_coherente",
            ),
        ]

    def __str__(self):
        return f"{self.reference_depense} - {self.action}"
