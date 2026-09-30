from rest_framework.routers import DefaultRouter
from . import views

app_name = "expenses_api"

router = DefaultRouter()
router.register("expenses", views.ExpenseViewSet, basename="expense")
router.register("categories", views.ExpenseCategoryViewSet, basename="expense-category")
router.register("cost-centers", views.CostCenterViewSet, basename="cost-center")
router.register("payments", views.ExpensePaymentViewSet, basename="expense-payment")
router.register("approvals", views.ExpenseApprovalViewSet, basename="expense-approval")
router.register("comments", views.ExpenseCommentViewSet, basename="expense-comment")
router.register("budgets", views.BudgetDepenseViewSet, basename="budget-depense")
router.register("advances", views.AvanceDepenseViewSet, basename="avance-depense")

urlpatterns = router.urls
