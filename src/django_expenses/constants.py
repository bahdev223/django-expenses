from django.utils.translation import gettext_lazy as _


class ExpenseStatus:
    DRAFT = "draft"
    SUBMITTED = "submitted"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"
    ARCHIVED = "archived"
    CANCELLED = "cancelled"

    CHOICES = [
        (DRAFT, _("Brouillon")),
        (SUBMITTED, _("Soumise")),
        (PENDING_APPROVAL, _("En attente d'approbation")),
        (APPROVED, _("Approuvée")),
        (REJECTED, _("Rejetée")),
        (PAID, _("Payée")),
        (ARCHIVED, _("Archivée")),
        (CANCELLED, _("Annulée")),
    ]

    TRANSITIONABLE = {DRAFT, SUBMITTED, PENDING_APPROVAL, REJECTED}
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
