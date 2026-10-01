from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from ..models import AvanceDepense, JustificationAvance
from ..signals import avance_creee, avance_justifiee, avance_soldee


class AvanceService:
    @staticmethod
    @transaction.atomic
    def creer(*, beneficiaire, montant_accorde, date_avance, objet, reference, cree_par,
              compte_reference="", notes="", entreprise_source="",
              entreprise_reference="", entreprise_libelle=""):
        montant_accorde = Decimal(str(montant_accorde))
        if montant_accorde <= 0:
            raise ValidationError("Le montant de l'avance doit être supérieur à zéro.")
        if bool(entreprise_source) != bool(entreprise_reference):
            raise ValidationError(
                "entreprise_source et entreprise_reference doivent être renseignés ensemble."
            )

        avance = AvanceDepense.objects.create(
            entreprise_source=entreprise_source,
            entreprise_reference=entreprise_reference,
            entreprise_libelle=entreprise_libelle,
            beneficiaire=beneficiaire,
            montant_accorde=montant_accorde,
            date_avance=date_avance,
            objet=objet,
            reference=reference,
            cree_par=cree_par,
            compte_reference=compte_reference,
            notes=notes,
        )
        avance_creee.send(sender=AvanceDepense, avance=avance, user=cree_par)
        return avance

    @staticmethod
    @transaction.atomic
    def ajouter_justification(avance, *, montant, date_depense, description, depense=None, piece=None, user=None):
        avance = AvanceDepense.objects.select_for_update().get(pk=avance.pk)
        if avance.statut in {AvanceDepense.Statut.SOLDEE, AvanceDepense.Statut.ANNULEE}:
            raise ValidationError("Cette avance ne peut plus être justifiée.")
        montant = Decimal(str(montant))
        if montant <= 0:
            raise ValidationError("Le montant justifié doit être supérieur à zéro.")
        if montant > avance.reste_a_justifier:
            raise ValidationError("Le montant justifié dépasse le reste à justifier.")

        if depense is not None and (
            depense.entreprise_source != avance.entreprise_source
            or depense.entreprise_reference != avance.entreprise_reference
        ):
            raise ValidationError(
                "La dépense utilisée pour justifier l'avance appartient à une autre entreprise."
            )

        justification = JustificationAvance.objects.create(
            avance=avance,
            montant=montant,
            date_depense=date_depense,
            description=description,
            depense=depense,
            piece=piece or "",
        )
        avance.refresh_from_db()
        if avance.reste_a_justifier == 0:
            avance.statut = AvanceDepense.Statut.JUSTIFIEE
        else:
            avance.statut = AvanceDepense.Statut.PARTIELLEMENT_JUSTIFIEE
        avance.save(update_fields=["statut", "modifie_le"])
        avance_justifiee.send(
            sender=AvanceDepense,
            avance=avance,
            justification=justification,
            user=user,
        )
        return justification

    @staticmethod
    @transaction.atomic
    def solder(avance, *, user=None):
        avance = AvanceDepense.objects.select_for_update().get(pk=avance.pk)
        if avance.reste_a_justifier != 0:
            raise ValidationError("L'avance ne peut être soldée tant qu'un montant reste à justifier.")
        avance.statut = AvanceDepense.Statut.SOLDEE
        avance.save(update_fields=["statut", "modifie_le"])
        avance_soldee.send(sender=AvanceDepense, avance=avance, user=user)
        return avance
