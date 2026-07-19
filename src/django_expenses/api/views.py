from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import DjangoModelPermissions

from ..models import (
    Expense,
    ExpenseCategory,
    ExpenseType,
    CostCenter,
    ExpenseAttachment,
    ExpenseApproval,
    ExpensePayment,
    ExpenseComment,
)
from ..services import ExpenseService, ReportService
from ..exceptions import WorkflowError
from .serializers import (
    ExpenseListSerializer,
    ExpenseDetailSerializer,
    ExpenseWriteSerializer,
    ExpenseCategorySerializer,
    ExpenseTypeSerializer,
    CostCenterSerializer,
    ExpenseAttachmentSerializer,
    ExpenseApprovalSerializer,
    ExpensePaymentSerializer,
    ExpenseCommentSerializer,
)


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.select_related(
        "user", "expense_type__category", "cost_center", "approved_by"
    ).prefetch_related("attachments", "approvals", "payments", "comments")
    permission_classes = [DjangoModelPermissions]
    filterset_fields = ["status", "expense_type", "cost_center", "currency", "user"]
    search_fields = ["reference_number", "description", "vendor"]

    def get_serializer_class(self):
        if self.action == "list":
            return ExpenseListSerializer
        if self.action in ("create", "update", "partial_update"):
            return ExpenseWriteSerializer
        return ExpenseDetailSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def _transition(self, request, pk, method, **kwargs):
        try:
            expense = self.get_object()
            result = method(expense, user=request.user, **kwargs)
            serializer = ExpenseDetailSerializer(result)
            return Response(serializer.data)
        except WorkflowError as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        return self._transition(request, pk, ExpenseService.submit)

    @action(detail=True, methods=["post"])
    def request_approval(self, request, pk=None):
        return self._transition(request, pk, ExpenseService.request_approval)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        return self._transition(
            request,
            pk,
            ExpenseService.approve,
            comment=request.data.get("comment", ""),
        )

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        return self._transition(
            request,
            pk,
            ExpenseService.reject,
            reason=request.data.get("reason", ""),
        )

    @action(detail=True, methods=["post"])
    def pay(self, request, pk=None):
        return self._transition(
            request, pk, ExpenseService.pay, payment_data=request.data
        )

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        return self._transition(request, pk, ExpenseService.cancel)

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        return self._transition(request, pk, ExpenseService.archive)

    @action(detail=False, methods=["get"])
    def report(self, request):
        from datetime import date
        start = request.query_params.get("start", str(date.today().replace(day=1)))
        end = request.query_params.get("end", str(date.today()))
        from datetime import datetime
        start_date = datetime.strptime(start, "%Y-%m-%d").date()
        end_date = datetime.strptime(end, "%Y-%m-%d").date()
        report = ReportService.generate_report(start_date, end_date)
        return Response(report)

    @action(detail=False, methods=["get"])
    def export(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        return ReportService.export_csv(queryset)


class ExpenseCategoryViewSet(viewsets.ModelViewSet):
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer
    permission_classes = [DjangoModelPermissions]


class ExpenseTypeViewSet(viewsets.ModelViewSet):
    queryset = ExpenseType.objects.select_related("category").all()
    serializer_class = ExpenseTypeSerializer
    permission_classes = [DjangoModelPermissions]
    filterset_fields = ["category", "is_active"]
    search_fields = ["name"]


class CostCenterViewSet(viewsets.ModelViewSet):
    queryset = CostCenter.objects.all()
    serializer_class = CostCenterSerializer
    permission_classes = [DjangoModelPermissions]
    search_fields = ["code", "name"]


class ExpensePaymentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ExpensePayment.objects.select_related("expense", "paid_by").all()
    serializer_class = ExpensePaymentSerializer
    filterset_fields = ["payment_method", "expense"]


class ExpenseApprovalViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ExpenseApproval.objects.select_related(
        "expense", "approved_by"
    ).all()
    serializer_class = ExpenseApprovalSerializer
    filterset_fields = ["decision", "expense"]


class ExpenseCommentViewSet(viewsets.ModelViewSet):
    queryset = ExpenseComment.objects.select_related("expense", "user").all()
    serializer_class = ExpenseCommentSerializer
    permission_classes = [DjangoModelPermissions]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
