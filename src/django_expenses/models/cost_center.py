from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class CostCenter(models.Model):
    entreprise_source = models.CharField(max_length=80, blank=True, db_index=True)
    entreprise_reference = models.CharField(max_length=120, blank=True, db_index=True)
    entreprise_libelle = models.CharField(max_length=240, blank=True)
    code = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_cost_centers",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code"]
        verbose_name = _("Cost center")
        verbose_name_plural = _("Cost centers")
        constraints = [
            models.UniqueConstraint(
                fields=["entreprise_source", "entreprise_reference", "code"],
                name="cost_center_code_par_entreprise",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(entreprise_source="", entreprise_reference="")
                    | (~models.Q(entreprise_source="") & ~models.Q(entreprise_reference=""))
                ),
                name="cost_center_entreprise_coherente",
            ),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"
