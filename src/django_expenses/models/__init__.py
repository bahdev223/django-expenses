from .category import ExpenseCategory
from .cost_center import CostCenter
from .expense import Expense
from .attachment import ExpenseAttachment
from .approval import ExpenseApproval
from .payment import ExpensePayment
from .comment import ExpenseComment
from .budget import BudgetDepense
from .advance import AvanceDepense, JustificationAvance
from .audit import EvenementDepense

# Façade française : les imports historiques restent supportés.
Depense = Expense
CategorieDepense = ExpenseCategory
CentreCout = CostCenter
PieceJointeDepense = ExpenseAttachment
ApprobationDepense = ExpenseApproval
PaiementDepense = ExpensePayment
CommentaireDepense = ExpenseComment

__all__ = [
    "Expense",
    "ExpenseCategory",
    "CostCenter",
    "ExpenseAttachment",
    "ExpenseApproval",
    "ExpensePayment",
    "ExpenseComment",
    "BudgetDepense",
    "AvanceDepense",
    "JustificationAvance",
    "EvenementDepense",
    "Depense",
    "CategorieDepense",
    "CentreCout",
    "PieceJointeDepense",
    "ApprobationDepense",
    "PaiementDepense",
    "CommentaireDepense",
]
