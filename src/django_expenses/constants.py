from django.utils.translation import gettext_lazy as _


class ExpenseStatus:
    DRAFT = "draft"
    SUBMITTED = "submitted"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    PARTIALLY_PAID = "partiellement_payee"
    PAID = "paid"
    ARCHIVED = "archived"
    CANCELLED = "cancelled"

    CHOICES = [
        (DRAFT, _("Brouillon")),
        (SUBMITTED, _("Soumise")),
        (PENDING_APPROVAL, _("En attente d'approbation")),
        (APPROVED, _("Approuvée")),
        (REJECTED, _("Rejetée")),
        (PARTIALLY_PAID, _("Partiellement payée")),
        (PAID, _("Payée")),
        (ARCHIVED, _("Archivée")),
        (CANCELLED, _("Annulée")),
    ]

    TRANSITIONABLE = {DRAFT, SUBMITTED, PENDING_APPROVAL, REJECTED, PARTIALLY_PAID}
    EDITABLE = {DRAFT, REJECTED}


class PaymentMethod:
    CASH = "cash"
    CHECK = "check"
    BANK_TRANSFER = "bank_transfer"
    MOBILE_MONEY = "mobile_money"
    CARD = "card"
    OTHER = "other"

    CHOICES = [
        (CASH, _("Espèces")),
        (CHECK, _("Chèque")),
        (BANK_TRANSFER, _("Virement bancaire")),
        (MOBILE_MONEY, _("Mobile Money")),
        (CARD, _("Carte bancaire")),
        (OTHER, _("Autre")),
    ]


class ExpenseNature:
    ACHAT = "achat"
    FONCTIONNEMENT = "fonctionnement"
    PERSONNEL = "personnel"
    MARKETING = "marketing"
    INVESTISSEMENT = "investissement"
    IMPOTS = "impots"
    DIVERS = "divers"

    CHOICES = [
        (ACHAT, _("Achats")),
        (FONCTIONNEMENT, _("Frais de fonctionnement")),
        (PERSONNEL, _("Personnel")),
        (MARKETING, _("Marketing et publicité")),
        (INVESTISSEMENT, _("Investissements")),
        (IMPOTS, _("Impôts et taxes")),
        (DIVERS, _("Divers")),
    ]


# Façade métier française. Les classes historiques restent disponibles pour compatibilité.
StatutDepense = ExpenseStatus
ModePaiement = PaymentMethod
NatureDepense = ExpenseNature


# Default expense categories — imported from data module for compatibility
from .data.default_categories import CATEGORIES as DEFAULT_EXPENSE_CATEGORIES, TEMPLATES  # noqa: E402, F401
