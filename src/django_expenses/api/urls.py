from rest_framework.routers import DefaultRouter
from . import views

app_name = "expenses_api"

router = DefaultRouter()
router.register("expenses", views.ExpenseViewSet)
router.register("categories", views.ExpenseCategoryViewSet)
router.register("cost-centers", views.CostCenterViewSet)
router.register("payments", views.ExpensePaymentViewSet)
router.register("approvals", views.ExpenseApprovalViewSet)
router.register("comments", views.ExpenseCommentViewSet)

urlpatterns = router.urls
