"""
Comprehensive OHADA-compatible expense categories.

Structure per entry (13 fields):
    code, name, parent_code, expense_nature, default_account_code,
    default_vat_rate, requires_approval, requires_receipt, requires_vendor,
    unit, icon, sort_order, depreciation_rate
"""

CATEGORIES = [
    # ═══════════════════════════════════════════════════════════════
    # 1. ACHATS
    # ═══════════════════════════════════════════════════════════════
    ("ACHAT", "Achats", None, "achat", "", 0, True, True, True, "", "fa-shopping-cart", 100, None),
    ("ACHAT_MATIERES_PREMIERES", "Matières premières", "ACHAT", "achat", "601", 18, True, True, True, "", "", 110, None),
    ("ACHAT_FOURNITURES", "Fournitures", "ACHAT", "achat", "602", 18, False, True, True, "", "", 120, None),
    ("ACHAT_EMBALLAGES", "Emballages", "ACHAT", "achat", "604", 18, False, True, True, "", "", 130, None),
    ("ACHAT_MARCHANDISES", "Marchandises", "ACHAT", "achat", "607", 18, True, True, True, "", "", 140, None),
    ("ACHAT_PETIT_EQUIPEMENT", "Petit équipement", "ACHAT", "achat", "606", 18, False, True, True, "", "", 150, None),

    # ─── Matières premières (601) ────────────────────────────────
    ("MP_FARINE", "Farine", "ACHAT_MATIERES_PREMIERES", "achat", "60101", 18, False, True, True, "kg", "fa-seedling", 111, None),
    ("MP_SUCRE", "Sucre", "ACHAT_MATIERES_PREMIERES", "achat", "60102", 18, False, True, True, "kg", "fa-cube", 112, None),
    ("MP_BEURRE", "Beurre", "ACHAT_MATIERES_PREMIERES", "achat", "60103", 18, False, True, True, "kg", "fa-square", 113, None),
    ("MP_OEUF", "Œufs", "ACHAT_MATIERES_PREMIERES", "achat", "60104", 18, False, True, True, "pièce", "fa-circle", 114, None),
    ("MP_LEVURE", "Levure", "ACHAT_MATIERES_PREMIERES", "achat", "60105", 18, False, True, True, "kg", "fa-biohazard", 115, None),
    ("MP_LAIT", "Lait", "ACHAT_MATIERES_PREMIERES", "achat", "60106", 18, False, True, True, "litre", "fa-tint", 116, None),
    ("MP_CHOCOLAT", "Chocolat", "ACHAT_MATIERES_PREMIERES", "achat", "60107", 18, False, True, True, "kg", "fa-heart", 117, None),
    ("MP_FRUITS", "Fruits", "ACHAT_MATIERES_PREMIERES", "achat", "60108", 18, False, True, True, "kg", "fa-apple-alt", 118, None),
    ("MP_AMANDES", "Amandes/Noix", "ACHAT_MATIERES_PREMIERES", "achat", "60109", 18, False, True, True, "kg", "fa-seedling", 119, None),
    ("MP_EPICES", "Épices", "ACHAT_MATIERES_PREMIERES", "achat", "60110", 18, False, True, True, "kg", "fa-pepper", 120, None),
    ("MP_HUILE", "Huile", "ACHAT_MATIERES_PREMIERES", "achat", "60111", 18, False, True, True, "litre", "fa-oil-can", 121, None),
    ("MP_SEL", "Sel", "ACHAT_MATIERES_PREMIERES", "achat", "60112", 18, False, True, True, "kg", "fa-cube", 122, None),
    ("MP_VANILLE", "Vanille", "ACHAT_MATIERES_PREMIERES", "achat", "60113", 18, False, True, True, "litre", "fa-flask", 123, None),
    ("MP_CREME", "Crème", "ACHAT_MATIERES_PREMIERES", "achat", "60114", 18, False, True, True, "litre", "fa-tint", 124, None),
    ("MP_CONFITURE", "Confiture", "ACHAT_MATIERES_PREMIERES", "achat", "60115", 18, False, True, True, "kg", "fa-jar", 125, None),
    ("MP_MIEL", "Miel", "ACHAT_MATIERES_PREMIERES", "achat", "60116", 18, False, True, True, "kg", "fa-jar", 126, None),
    ("MP_CACAO", "Cacao", "ACHAT_MATIERES_PREMIERES", "achat", "60117", 18, False, True, True, "kg", "fa-seedling", 127, None),
    ("MP_NOIX_COCO", "Noix de coco", "ACHAT_MATIERES_PREMIERES", "achat", "60118", 18, False, True, True, "kg", "fa-seedling", 128, None),
    ("MP_SIROP", "Sirop", "ACHAT_MATIERES_PREMIERES", "achat", "60119", 18, False, True, True, "litre", "fa-tint", 129, None),
    ("MP_FROMAGE", "Fromage", "ACHAT_MATIERES_PREMIERES", "achat", "60120", 18, False, True, True, "kg", "fa-square", 130, None),

    # ─── Fournitures (602) ──────────────────────────────────────
    ("FOURN_PAPIER_CUISSON", "Papier cuisson", "ACHAT_FOURNITURES", "achat", "60201", 18, False, True, True, "rouleau", "fa-scroll", 131, None),
    ("FOURN_FILM", "Film alimentaire", "ACHAT_FOURNITURES", "achat", "60202", 18, False, True, True, "rouleau", "fa-film", 132, None),
    ("FOURN_ALUMINIUM", "Papier aluminium", "ACHAT_FOURNITURES", "achat", "60203", 18, False, True, True, "rouleau", "fa-scroll", 133, None),
    ("FOURN_GANTS", "Gants", "ACHAT_FOURNITURES", "achat", "60204", 18, False, True, True, "pièce", "fa-hand-peace", 134, None),
    ("FOURN_EPONGES", "Éponges", "ACHAT_FOURNITURES", "achat", "60205", 18, False, True, True, "pièce", "fa-sponge", 135, None),
    ("FOURN_NETTOYANT", "Produits nettoyants", "ACHAT_FOURNITURES", "achat", "60206", 18, False, True, True, "litre", "fa-broom", 136, None),
    ("FOURN_DESINFECTANT", "Désinfectants", "ACHAT_FOURNITURES", "achat", "60207", 18, False, True, True, "litre", "fa-shield", 137, None),
    ("FOURN_SAVON", "Savon", "ACHAT_FOURNITURES", "achat", "60208", 18, False, True, True, "pièce", "fa-hand-wash", 138, None),
    ("FOURN_PAPIER_TOILETTE", "Papier toilette", "ACHAT_FOURNITURES", "achat", "60209", 18, False, True, True, "rouleau", "fa-toilet", 139, None),
    ("FOURN_ESSUIE_TOUT", "Essuie-tout", "ACHAT_FOURNITURES", "achat", "60210", 18, False, True, True, "rouleau", "fa-towel", 140, None),
    ("FOURN_SACS_POUBELLE", "Sacs poubelle", "ACHAT_FOURNITURES", "achat", "60211", 18, False, True, True, "rouleau", "fa-trash", 141, None),
    ("FOURN_BALAIS", "Balais/Serpillières", "ACHAT_FOURNITURES", "achat", "60212", 18, False, True, True, "pièce", "fa-broom", 142, None),
    ("FOURN_BROSSES", "Brosses", "ACHAT_FOURNITURES", "achat", "60213", 18, False, True, True, "pièce", "fa-brush", 143, None),
    ("FOURN_COUTEAUX", "Couteaux", "ACHAT_FOURNITURES", "achat", "60215", 18, False, True, True, "pièce", "fa-cut", 145, None),
    ("FOURN_PLANCHES", "Planches à découper", "ACHAT_FOURNITURES", "achat", "60216", 18, False, True, True, "pièce", "fa-kitchen-set", 146, None),
    ("FOURN_BOLS", "Bols de pesée", "ACHAT_FOURNITURES", "achat", "60223", 18, False, True, True, "pièce", "fa-bowl", 153, None),
    ("FOURN_TAMIS", "Tamis", "ACHAT_FOURNITURES", "achat", "60224", 18, False, True, True, "pièce", "fa-sieve", 154, None),
    ("FOURN_RAPES", "Râpes", "ACHAT_FOURNITURES", "achat", "60225", 18, False, True, True, "pièce", "fa-grater", 155, None),
    ("FOURN_THERMOMETRES", "Thermomètres", "ACHAT_FOURNITURES", "achat", "60229", 18, False, True, True, "pièce", "fa-thermometer", 159, None),
    ("FOURN_SPATULES", "Spatules", "ACHAT_FOURNITURES", "achat", "60221", 18, False, True, True, "pièce", "fa-spatula", 151, None),
    ("FOURN_FOUETS", "Fouets", "ACHAT_FOURNITURES", "achat", "60222", 18, False, True, True, "pièce", "fa-whisk", 152, None),

    # ─── Emballages (604) ───────────────────────────────────────
    ("EMB_SACS_PAPIER", "Sacs en papier", "ACHAT_EMBALLAGES", "achat", "60401", 18, False, True, True, "pièce", "fa-bag-shopping", 160, None),
    ("EMB_BOITES_PATISSERIE", "Boîtes à pâtisserie", "ACHAT_EMBALLAGES", "achat", "60403", 18, False, True, True, "pièce", "fa-box-open", 162, None),
    ("EMB_BOITES_GATEAUX", "Boîtes à gâteaux", "ACHAT_EMBALLAGES", "achat", "60405", 18, False, True, True, "pièce", "fa-box-open", 164, None),
    ("EMB_BARQUETTES", "Barquettes", "ACHAT_EMBALLAGES", "achat", "60407", 18, False, True, True, "pièce", "fa-box", 166, None),
    ("EMB_ETIQUETTES", "Étiquettes", "ACHAT_EMBALLAGES", "achat", "60411", 18, False, True, True, "pièce", "fa-tag", 170, None),
    ("EMB_RUBAN", "Ruban adhésif", "ACHAT_EMBALLAGES", "achat", "60412", 18, False, True, True, "rouleau", "fa-tape", 171, None),
    ("EMB_SERVIETTES", "Serviettes en papier", "ACHAT_EMBALLAGES", "achat", "60414", 18, False, True, True, "pièce", "fa-napkin", 173, None),
    ("EMB_COUVERTS", "Couverts en plastique", "ACHAT_EMBALLAGES", "achat", "60415", 18, False, True, True, "pièce", "fa-utensils", 174, None),
    ("EMB_VERRES", "Verres en plastique", "ACHAT_EMBALLAGES", "achat", "60416", 18, False, True, True, "pièce", "fa-glass", 175, None),
    ("EMB_ASSIETTES", "Assiettes en carton", "ACHAT_EMBALLAGES", "achat", "60417", 18, False, True, True, "pièce", "fa-plate", 176, None),
    ("EMB_MOULES", "Moules à gâteaux", "ACHAT_EMBALLAGES", "achat", "60418", 18, False, True, True, "pièce", "fa-muffin", 177, None),
    ("EMB_CAISSETTES", "Caissettes", "ACHAT_EMBALLAGES", "achat", "60421", 18, False, True, True, "pièce", "fa-box", 180, None),
    ("EMB_PAPIER_CADEAU", "Papier cadeau", "ACHAT_EMBALLAGES", "achat", "60424", 18, False, True, True, "rouleau", "fa-gift", 183, None),
    ("EMB_CARTONS", "Cartons de transport", "ACHAT_EMBALLAGES", "achat", "60425", 18, False, True, True, "pièce", "fa-box", 184, None),
    ("EMB_FILMS", "Films transparents", "ACHAT_EMBALLAGES", "achat", "60408", 18, False, True, True, "rouleau", "fa-film", 167, None),

    # ═══════════════════════════════════════════════════════════════
    # 2. FRAIS DE FONCTIONNEMENT
    # ═══════════════════════════════════════════════════════════════
    ("FONCTIONNEMENT", "Frais de fonctionnement", None, "fonctionnement", "", 0, True, True, True, "", "fa-cogs", 200, None),

    # ─── Énergie (614) ──────────────────────────────────────────
    ("FONCT_EAU", "Eau", "FONCTIONNEMENT", "fonctionnement", "61401", 18, True, True, True, "", "fa-water", 210, None),
    ("FONCT_ELECTRICITE", "Électricité", "FONCTIONNEMENT", "fonctionnement", "61402", 18, True, True, True, "", "fa-bolt", 211, None),
    ("FONCT_GAZ", "Gaz", "FONCTIONNEMENT", "fonctionnement", "61403", 18, True, True, True, "", "fa-fire", 212, None),
    ("FONCT_INTERNET", "Internet/Wi-Fi", "FONCTIONNEMENT", "fonctionnement", "61404", 18, True, True, True, "", "fa-wifi", 213, None),
    ("FONCT_TELEPHONE", "Téléphone", "FONCTIONNEMENT", "fonctionnement", "60606", 18, False, True, True, "", "fa-phone", 214, None),
    ("FONCT_LOYER", "Loyer", "FONCTIONNEMENT", "fonctionnement", "613", 18, True, True, True, "", "fa-building", 220, None),
    ("FONCT_ENTRETIEN", "Entretien et réparations", "FONCTIONNEMENT", "fonctionnement", "612", 18, True, True, True, "", "fa-wrench", 230, None),
    ("FONCT_TRANSPORT", "Transport", "FONCTIONNEMENT", "fonctionnement", "611", 18, True, True, True, "", "fa-truck", 240, None),
    ("FONCT_CARBURANT", "Carburant", "FONCTIONNEMENT", "fonctionnement", "61101", 18, True, True, True, "", "fa-gas-pump", 241, None),
    ("FONCT_ASSURANCE", "Assurances", "FONCTIONNEMENT", "fonctionnement", "608", 18, True, True, True, "", "fa-shield", 250, None),
    ("FONCT_POSTAUX", "Frais postaux", "FONCTIONNEMENT", "fonctionnement", "622", 18, False, True, True, "", "fa-envelope", 260, None),

    # ─── Sous-catégories Transport (611) ─────────────────────────
    ("TRANS_CARBURANT", "Carburant", "FONCT_TRANSPORT", "fonctionnement", "61101", 18, True, True, True, "", "fa-gas-pump", 242, None),
    ("TRANS_ENTRETIEN", "Entretien véhicule", "FONCT_TRANSPORT", "fonctionnement", "61102", 18, False, True, True, "", "fa-oil-can", 243, None),
    ("TRANS_REPARATION", "Réparation véhicule", "FONCT_TRANSPORT", "fonctionnement", "61103", 18, False, True, True, "", "fa-wrench", 244, None),
    ("TRANS_ASSURANCE", "Assurance véhicule", "FONCT_TRANSPORT", "fonctionnement", "61104", 18, True, True, True, "", "fa-shield", 245, None),
    ("TRANS_LOCATION", "Location véhicule", "FONCT_TRANSPORT", "fonctionnement", "61105", 18, True, True, True, "", "fa-car", 246, None),
    ("TRANS_PEAGES", "Péages", "FONCT_TRANSPORT", "fonctionnement", "61110", 18, False, True, True, "", "fa-road", 247, None),
    ("TRANS_STATIONNEMENT", "Stationnement", "FONCT_TRANSPORT", "fonctionnement", "61111", 18, False, True, True, "", "fa-parking", 248, None),
    ("TRANS_LIVRAISON", "Livraison express", "FONCT_TRANSPORT", "fonctionnement", "61113", 18, False, True, True, "", "fa-truck-fast", 249, None),

    # ─── Sous-catégories Entretien (612) ─────────────────────────
    ("ENTRET_FOUR", "Réparation fours", "FONCT_ENTRETIEN", "fonctionnement", "61201", 18, False, True, True, "", "fa-oven", 231, None),
    ("ENTRET_CHAMBRE_FROID", "Réparation chambres froides", "FONCT_ENTRETIEN", "fonctionnement", "61204", 18, False, True, True, "", "fa-snowflake", 232, None),
    ("ENTRET_PLOMBERIE", "Réparation plomberie", "FONCT_ENTRETIEN", "fonctionnement", "61205", 18, False, True, True, "", "fa-wrench", 233, None),
    ("ENTRET_ELECTRICITE", "Réparation électricité", "FONCT_ENTRETIEN", "fonctionnement", "61206", 18, False, True, True, "", "fa-bolt", 234, None),
    ("ENTRET_CLIMATISATION", "Réparation climatisation", "FONCT_ENTRETIEN", "fonctionnement", "61207", 18, False, True, True, "", "fa-snowflake", 235, None),
    ("ENTRET_INFORMATIQUE", "Réparation informatique", "FONCT_ENTRETIEN", "fonctionnement", "61214", 18, False, True, True, "", "fa-laptop", 236, None),
    ("ENTRET_NETTOYAGE_PRO", "Nettoyage professionnel", "FONCT_ENTRETIEN", "fonctionnement", "61221", 18, False, True, True, "", "fa-broom", 237, None),
    ("ENTRET_DESINFECTION", "Désinfection", "FONCT_ENTRETIEN", "fonctionnement", "61222", 18, False, True, True, "", "fa-shield", 238, None),

    # ─── Sous-catégories Loyer (613) ────────────────────────────
    ("LOYER_BOUTIQUE", "Loyer boutique", "FONCT_LOYER", "fonctionnement", "61301", 18, True, True, True, "", "fa-store", 221, None),
    ("LOYER_ATELIER", "Loyer atelier", "FONCT_LOYER", "fonctionnement", "61302", 18, True, True, True, "", "fa-warehouse", 222, None),
    ("LOYER_STOCKAGE", "Loyer stockage", "FONCT_LOYER", "fonctionnement", "61303", 18, True, True, True, "", "fa-warehouse", 223, None),
    ("LOYER_BUREAU", "Loyer bureau", "FONCT_LOYER", "fonctionnement", "61304", 18, True, True, True, "", "fa-building", 224, None),
    ("LOYER_CHARGES", "Charges locatives", "FONCT_LOYER", "fonctionnement", "61305", 18, True, True, True, "", "fa-building", 225, None),

    # ─── Énergie (614) sous-catégories ──────────────────────────
    ("ENERGIE_EAU", "Eau", "FONCT_EAU", "fonctionnement", "61401", 18, True, True, True, "", "fa-water", 210, None),
    ("ENERGIE_ELECTRICITE", "Électricité", "FONCT_ELECTRICITE", "fonctionnement", "61402", 18, True, True, True, "", "fa-bolt", 211, None),
    ("ENERGIE_GAZ", "Gaz", "FONCT_GAZ", "fonctionnement", "61403", 18, True, True, True, "", "fa-fire", 212, None),
    ("ENERGIE_CHAUFFAGE", "Gaz (chauffage)", "FONCT_GAZ", "fonctionnement", "61404", 18, True, True, True, "", "fa-fire", 213, None),
    ("ENERGIE_CLIMATISATION", "Climatisation", "FONCTIONNEMENT", "fonctionnement", "61409", 18, False, True, True, "", "fa-snowflake", 215, None),

    # ─── Frais postaux (622) sous-catégories ─────────────────────
    ("POSTE_AFFRANCHISSEMENT", "Affranchissement", "FONCT_POSTAUX", "fonctionnement", "62201", 18, False, True, True, "", "fa-envelope", 261, None),
    ("POSTE_COLIS", "Colis", "FONCT_POSTAUX", "fonctionnement", "62202", 18, False, True, True, "", "fa-box", 262, None),
    ("POSTE_RECOMMANDE", "Recommandés", "FONCT_POSTAUX", "fonctionnement", "62203", 18, False, True, True, "", "fa-envelope", 263, None),
    ("POSTE_MESSAGERIE", "Messagerie", "FONCT_POSTAUX", "fonctionnement", "62206", 18, False, True, True, "", "fa-truck", 264, None),

    # ═══════════════════════════════════════════════════════════════
    # 3. PERSONNEL
    # ═══════════════════════════════════════════════════════════════
    ("PERSONNEL", "Personnel", None, "personnel", "", 0, True, True, True, "", "fa-users", 300, None),
    ("PERS_SALAIRES", "Salaires", "PERSONNEL", "personnel", "641", 0, True, False, False, "", "fa-money-bill", 310, None),
    ("PERS_PRIMES", "Primes", "PERSONNEL", "personnel", "64104", 0, True, False, False, "", "fa-star", 320, None),
    ("PERS_INDEMNITES", "Indemnités", "PERSONNEL", "personnel", "64105", 0, True, False, False, "", "fa-hand-holding-usd", 330, None),
    ("PERS_CHARGES_SOCIALES", "Charges sociales", "PERSONNEL", "personnel", "642", 0, True, False, False, "", "fa-shield", 340, None),
    ("PERS_FORMATION", "Formation", "PERSONNEL", "personnel", "60507", 18, True, True, True, "", "fa-graduation-cap", 350, None),
    ("PERS_MEDECINE", "Médecine du travail", "PERSONNEL", "personnel", "64106", 0, False, True, True, "", "fa-medkit", 360, None),
    ("PERS_RESTAURATION", "Restauration du personnel", "PERSONNEL", "personnel", "64107", 0, False, True, True, "", "fa-utensils", 370, None),
    ("PERS_TRANSPORT", "Transport du personnel", "PERSONNEL", "personnel", "64108", 0, False, True, True, "", "fa-bus", 380, None),

    # ─── Salaires (641) sous-catégories ─────────────────────────
    ("SAL_BOULANGER", "Boulangers", "PERS_SALAIRES", "personnel", "64101", 0, True, False, False, "", "fa-bread-slice", 311, None),
    ("SAL_PATISSIER", "Pâtissiers", "PERS_SALAIRES", "personnel", "64102", 0, True, False, False, "", "fa-cake", 312, None),
    ("SAL_VENDEUR", "Vendeurs", "PERS_SALAIRES", "personnel", "64103", 0, True, False, False, "", "fa-user", 313, None),
    ("SAL_LIVREUR", "Livreurs", "PERS_SALAIRES", "personnel", "64104", 0, True, False, False, "", "fa-truck", 314, None),
    ("SAL_COMPTABLE", "Comptables", "PERS_SALAIRES", "personnel", "64106", 0, True, False, False, "", "fa-calculator", 315, None),
    ("SAL_DIRECTEUR", "Directeurs", "PERS_SALAIRES", "personnel", "64105", 0, True, False, False, "", "fa-user-tie", 316, None),
    ("SAL_NETTOYAGE", "Agents de nettoyage", "PERS_SALAIRES", "personnel", "64108", 0, True, False, False, "", "fa-broom", 317, None),
    ("SAL_TECHNICIEN", "Techniciens", "PERS_SALAIRES", "personnel", "64110", 0, True, False, False, "", "fa-tools", 318, None),
    ("SAL_STAGIAIRE", "Stagiaires", "PERS_SALAIRES", "personnel", "64111", 0, True, False, False, "", "fa-user-graduate", 319, None),
    ("SAL_HEURES_SUP", "Heures supplémentaires", "PERS_SALAIRES", "personnel", "64115", 0, True, False, False, "", "fa-clock", 320, None),
    ("SAL_PRIMES", "Primes", "PERS_PRIMES", "personnel", "64113", 0, True, False, False, "", "fa-star", 321, None),
    ("SAL_13EME_MOIS", "13ème mois", "PERS_PRIMES", "personnel", "64117", 0, True, False, False, "", "fa-gift", 322, None),
    ("SAL_INDEMNITES", "Indemnités", "PERS_INDEMNITES", "personnel", "64114", 0, True, False, False, "", "fa-money-bill", 331, None),

    # ─── Charges sociales (642) sous-catégories ─────────────────
    ("CS_CNSS_PATRONALE", "CNSS patronale", "PERS_CHARGES_SOCIALES", "personnel", "64201", 0, True, False, False, "", "fa-shield", 341, None),
    ("CS_CNSS_SALARIALE", "CNSS salariale", "PERS_CHARGES_SOCIALES", "personnel", "64202", 0, True, False, False, "", "fa-shield", 342, None),
    ("CS_ASSURANCE_MALADIE", "Assurance maladie", "PERS_CHARGES_SOCIALES", "personnel", "64203", 0, True, False, False, "", "fa-heartbeat", 343, None),
    ("CS_RETRAITE", "Retraite complémentaire", "PERS_CHARGES_SOCIALES", "personnel", "64205", 0, True, False, False, "", "fa-user-clock", 344, None),
    ("CS_MUTUELLE", "Mutuelle", "PERS_CHARGES_SOCIALES", "personnel", "64207", 0, True, False, False, "", "fa-hand-holding-heart", 345, None),

    # ═══════════════════════════════════════════════════════════════
    # 4. MARKETING ET PUBLICITÉ
    # ═══════════════════════════════════════════════════════════════
    ("MARKETING", "Marketing et publicité", None, "marketing", "", 0, True, True, True, "", "fa-bullhorn", 400, None),
    ("MARK_PUBLICITE", "Publicité", "MARKETING", "marketing", "621", 18, True, True, True, "", "fa-bullhorn", 410, None),
    ("MARK_FACEBOOK", "Facebook Ads", "MARKETING", "marketing", "62101", 18, True, True, True, "", "fa-facebook", 411, None),
    ("MARK_GOOGLE", "Google Ads", "MARKETING", "marketing", "62102", 18, True, True, True, "", "fa-google", 412, None),
    ("MARK_IMPRESSION", "Impression", "MARKETING", "marketing", "62103", 18, False, True, True, "", "fa-print", 413, None),
    ("MARK_RADIO", "Radio", "MARKETING", "marketing", "62104", 18, True, True, True, "", "fa-radio", 414, None),
    ("MARK_TELEVISION", "Télévision", "MARKETING", "marketing", "62105", 18, True, True, True, "", "fa-tv", 415, None),
    ("MARK_AFFICHAGE", "Affichage", "MARKETING", "marketing", "62106", 18, False, True, True, "", "fa-bullhorn", 416, None),
    ("MARK_WEBSITE", "Site web", "MARKETING", "marketing", "62107", 18, True, True, True, "", "fa-globe", 417, None),
    ("MARK_RELATIONS_PUBLIQUES", "Relations publiques", "MARKETING", "marketing", "62108", 18, True, True, True, "", "fa-handshake", 418, None),

    # ─── Publicité (621) sous-catégories ────────────────────────
    ("PUB_RADIO", "Publicité radio", "MARK_RADIO", "marketing", "62101", 18, True, True, True, "", "fa-radio", 414, None),
    ("PUB_TELEVISION", "Publicité télévision", "MARK_TELEVISION", "marketing", "62102", 18, True, True, True, "", "fa-tv", 415, None),
    ("PUB_RESEAUX_SOCIAUX", "Publicité réseaux sociaux", "MARK_FACEBOOK", "marketing", "62105", 18, True, True, True, "", "fa-share", 411, None),
    ("PUB_FLYERS", "Flyers", "MARK_IMPRESSION", "marketing", "62107", 18, False, True, True, "", "fa-hand", 413, None),
    ("PUB_AGENCE", "Agence publicitaire", "MARK_PUBLICITE", "marketing", "62111", 18, True, True, True, "", "fa-bullhorn", 418, None),
    ("PUB_REFERENCEMENT", "Référencement", "MARK_WEBSITE", "marketing", "62113", 18, True, True, True, "", "fa-search", 419, None),

    # ═══════════════════════════════════════════════════════════════
    # 5. INVESTISSEMENTS
    # ═══════════════════════════════════════════════════════════════
    ("INVESTISSEMENT", "Investissements", None, "investissement", "", 0, True, True, True, "", "fa-chart-line", 500, None),
    ("INV_TERRAIN", "Terrains", "INVESTISSEMENT", "investissement", "211", 0, True, True, True, "", "fa-mountain", 510, None),
    ("INV_BATIMENT", "Bâtiments", "INVESTISSEMENT", "investissement", "212", 18, True, True, True, "", "fa-building", 520, None),
    ("INV_EQUIPEMENT", "Équipements", "INVESTISSEMENT", "investissement", "215", 18, True, True, True, "", "fa-cogs", 530, None),
    ("INV_VEHICULE", "Véhicules", "INVESTISSEMENT", "investissement", "218", 18, True, True, True, "", "fa-car", 540, None),
    ("INV_INFORMATIQUE", "Informatique", "INVESTISSEMENT", "investissement", "217", 18, True, True, True, "", "fa-laptop", 550, None),
    ("INV_MOBILIER", "Mobilier", "INVESTISSEMENT", "investissement", "219", 18, True, True, True, "", "fa-chair", 560, None),
    ("INV_LOGICIEL", "Logiciels", "INVESTISSEMENT", "investissement", "21801", 18, True, True, True, "", "fa-code", 570, None),

    # ═══════════════════════════════════════════════════════════════
    # 6. IMPÔTS ET TAXES
    # ═══════════════════════════════════════════════════════════════
    ("IMPOTS", "Impôts et taxes", None, "impots", "", 0, True, True, False, "", "fa-file-invoice-dollar", 600, None),
    ("IMP_IRPP", "IRPP", "IMPOTS", "impots", "63101", 0, True, True, False, "", "fa-file-invoice", 610, None),
    ("IMP_CNSS", "CNSS", "IMPOTS", "impots", "63102", 0, True, True, False, "", "fa-shield", 620, None),
    ("IMP_TAXE_SALAIRE", "Taxe sur salaires", "IMPOTS", "impots", "63105", 0, True, True, False, "", "fa-file-invoice", 630, None),
    ("IMP_TAXE_PROFESSIONNELLE", "Taxe professionnelle", "IMPOTS", "impots", "632", 0, True, True, False, "", "fa-briefcase", 640, None),
    ("IMP_TVA", "TVA", "IMPOTS", "impots", "633", 0, True, True, False, "", "fa-percent", 650, None),
    ("IMP_TAXE_FONCIERE", "Taxe foncière", "IMPOTS", "impots", "634", 0, True, True, False, "", "fa-landmark", 660, None),
    ("IMP_TAXE_ORDURES", "Taxe sur les ordures", "IMPOTS", "impots", "635", 0, False, True, False, "", "fa-trash", 670, None),

    # ─── Impôts (631) sous-catégories ──────────────────────────
    ("IMP_IRPP_DETAIL", "IRPP", "IMP_IRPP", "impots", "63101", 0, True, True, False, "", "fa-file-invoice-dollar", 611, None),
    ("IMP_CNSS_DETAIL", "CNSS", "IMP_CNSS", "impots", "63102", 0, True, True, False, "", "fa-shield", 621, None),
    ("IMP_IS", "Impôt sur les sociétés", "IMPOTS", "impots", "63106", 0, True, True, False, "", "fa-building", 680, None),

    # ═══════════════════════════════════════════════════════════════
    # 7. DIVERS
    # ═══════════════════════════════════════════════════════════════
    ("DIVERS", "Divers", None, "divers", "", 0, True, True, True, "", "fa-ellipsis-h", 700, None),
    ("DIV_BANCAIRE", "Frais bancaires", "DIVERS", "divers", "651", 0, False, True, False, "", "fa-university", 710, None),
    ("DIV_DONS", "Dons", "DIVERS", "divers", "652", 0, True, True, True, "", "fa-hand-holding-heart", 720, None),
    ("DIV_JURIDIQUE", "Frais juridiques", "DIVERS", "divers", "653", 18, True, True, True, "", "fa-gavel", 730, None),
    ("DIV_MEDICAMENTS", "Médicaments", "DIVERS", "divers", "654", 18, False, True, True, "", "fa-medkit", 740, None),
    ("DIV_DECORATION", "Décoration", "DIVERS", "divers", "655", 18, False, True, True, "", "fa-paint-roller", 750, None),
    ("DIV_CADEAUX", "Cadeaux", "DIVERS", "divers", "656", 18, False, True, True, "", "fa-gift", 760, None),

    # ─── Frais bancaires (651) sous-catégories ─────────────────
    ("BANQUE_COMMISSIONS", "Commissions bancaires", "DIV_BANCAIRE", "divers", "65101", 0, False, True, False, "", "fa-coins", 711, None),
    ("BANQUE_TENUE_COMPTE", "Frais de tenue de compte", "DIV_BANCAIRE", "divers", "65102", 0, False, True, False, "", "fa-university", 712, None),
    ("BANQUE_CARTE", "Frais de carte bancaire", "DIV_BANCAIRE", "divers", "65103", 0, False, True, False, "", "fa-credit-card", 713, None),
    ("BANQUE_VIREMENT", "Frais de virement", "DIV_BANCAIRE", "divers", "65104", 0, False, True, False, "", "fa-exchange", 714, None),
    ("BANQUE_INTERETS", "Intérêts bancaires", "DIV_BANCAIRE", "divers", "65107", 0, False, True, False, "", "fa-percent", 715, None),

    # ─── Dons (652) sous-catégories ────────────────────────────
    ("DON_ASSOCIATION", "Dons aux associations", "DIV_DONS", "divers", "65201", 0, True, True, True, "", "fa-hand-holding-heart", 721, None),
    ("DON_OEUVRES", "Dons aux œuvres", "DIV_DONS", "divers", "65202", 0, True, True, True, "", "fa-hand-holding-heart", 722, None),
    ("DON_ECOLES", "Dons aux écoles", "DIV_DONS", "divers", "65203", 0, True, True, True, "", "fa-school", 723, None),
    ("DON_HOPITAUX", "Dons aux hôpitaux", "DIV_DONS", "divers", "65204", 0, True, True, True, "", "fa-hospital", 724, None),

    # ═══════════════════════════════════════════════════════════════
    # AMORTISSEMENTS (661) — transversal
    # ═══════════════════════════════════════════════════════════════
    ("AMORT_FOUR", "Amortissement fours", "INV_EQUIPEMENT", "investissement", "66101", 0, True, True, True, "", "fa-oven", 531, 10),
    ("AMORT_VEHICULE", "Amortissement véhicules", "INV_VEHICULE", "investissement", "66106", 0, True, True, True, "", "fa-car", 541, 20),
    ("AMORT_MOBILIER", "Amortissement mobilier", "INV_MOBILIER", "investissement", "66107", 0, True, True, True, "", "fa-chair", 561, 10),
    ("AMORT_INFORMATIQUE", "Amortissement informatique", "INV_INFORMATIQUE", "investissement", "66108", 0, True, True, True, "", "fa-laptop", 551, 20),
    ("AMORT_BATIMENT", "Amortissement bâtiments", "INV_BATIMENT", "investissement", "66109", 0, True, True, True, "", "fa-building", 521, 5),
    ("AMORT_AGENCEMENT", "Amortissement agencements", "INV_BATIMENT", "investissement", "66110", 0, True, True, True, "", "fa-tools", 522, 10),
]


TEMPLATES = {
    "default": {
        "label": "Catégories par défaut",
        "description": "Jeu de catégories complet compatible OHADA avec ~200 entrées",
        "categories": CATEGORIES,
    },
    "ohada": {
        "label": "SYSCOHADA complet",
        "description": "Catégories alignées sur le plan comptable SYSCOHADA",
        "categories": CATEGORIES,
    },
    "light": {
        "label": "Version légère",
        "description": "Catégories principales uniquement (sans sous-catégories)",
        "categories": [c for c in CATEGORIES if c[2] is None or not c[0].startswith(("MP_", "FOURN_", "EMB_", "TRANS_", "ENTRET_", "LOYER_", "ENERGIE_", "POSTE_", "PUB_", "SAL_", "CS_", "BANQUE_", "DON_", "AMORT_"))],
    },
}
