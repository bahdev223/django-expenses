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


class ExpenseNature:
    """Nature (type) of expense: fonctionnement, investissement, mission, achat."""
    OPERATING = "operating"
    INVESTMENT = "investment"
    MISSION = "mission"
    PURCHASE = "purchase"
    PAYROLL = "payroll"
    OTHER = "other"

    CHOICES = [
        (OPERATING, _("Fonctionnement")),
        (INVESTMENT, _("Investissement")),
        (MISSION, _("Mission")),
        (PURCHASE, _("Achat")),
        (PAYROLL, _("Personnel")),
        (OTHER, _("Autre")),
    ]


DEFAULT_EXPENSE_CATEGORIES = [
    # (code, name, parent_code, expense_nature, default_account_code, sort_order)
    ("ACHATS", "Achats", None, "purchase", "", 10),
    ("ACH_FOURNITURES", "Fournitures de bureau", "ACHATS", "purchase", "602", 11),
    ("ACH_MATIERES", "Matières premières", "ACHATS", "purchase", "601", 12),
    ("ACH_PETIT_MATERIEL", "Petit matériel", "ACHATS", "purchase", "602", 13),

    ("TRANSPORT", "Transport", None, "operating", "", 20),
    ("TRP_CARBURANT", "Carburant", "TRANSPORT", "operating", "6251", 21),
    ("TRP_TAXI", "Taxi", "TRANSPORT", "operating", "6252", 22),
    ("TRP_AVION", "Billets d'avion", "TRANSPORT", "mission", "6254", 23),
    ("TRP_PEAGE", "Péage", "TRANSPORT", "operating", "6255", 24),

    ("PERSONNEL", "Personnel", None, "payroll", "", 30),
    ("PRS_SALAIRES", "Salaires", "PERSONNEL", "payroll", "661", 31),
    ("PRS_PRIMES", "Primes", "PERSONNEL", "payroll", "661", 32),
    ("PRS_FORMATIONS", "Formations", "PERSONNEL", "payroll", "663", 33),

    ("MARKETING", "Marketing", None, "operating", "", 40),
    ("MKT_FACEBOOK", "Facebook Ads", "MARKETING", "operating", "623", 41),
    ("MKT_GOOGLE", "Google Ads", "MARKETING", "operating", "623", 42),
    ("MKT_IMPRESSION", "Impression", "MARKETING", "operating", "623", 43),

    ("ENERGIE", "Énergie", None, "operating", "", 50),
    ("ENR_EAU", "Eau", "ENERGIE", "operating", "605", 51),
    ("ENR_ELECTRICITE", "Électricité", "ENERGIE", "operating", "6052", 52),
    ("ENR_INTERNET", "Internet", "ENERGIE", "operating", "626", 53),

    ("MAINTENANCE", "Maintenance", None, "operating", "", 60),
    ("MNT_VEHICULES", "Véhicules", "MAINTENANCE", "operating", "615", 61),
    ("MNT_INFORMATIQUE", "Informatique", "MAINTENANCE", "operating", "615", 62),
    ("MNT_BATIMENTS", "Bâtiments", "MAINTENANCE", "operating", "615", 63),

    ("LOYERS", "Loyers", None, "operating", "613", 70),
    ("ASSURANCES", "Assurances", None, "operating", "616", 80),
    ("FRAIS_BANCAIRES", "Frais bancaires", None, "operating", "631", 90),
    ("FRAIS_JURIDIQUES", "Frais juridiques", None, "operating", "622", 100),
    ("IMPOTS_TAXES", "Impôts et taxes", None, "operating", "641", 110),
]
