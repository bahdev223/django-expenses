from datetime import date, datetime

from django.core.exceptions import PermissionDenied, ValidationError as DjangoValidationError
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from ..exceptions import WorkflowError
from ..hooks import HookRegistry
from ..settings import EXPENSES
from ..tenancy import (
    filtrer_par_entreprise,
    resoudre_entreprise,
    verifier_appartenance,
)
from ..models import (
    Expense,
    ExpenseCategory,
    CostCenter,
    ExpenseApproval,
    ExpensePayment,
    ExpenseComment,
    BudgetDepense,
    AvanceDepense,
)
from ..permissions import (
    CHANGE_EXPENSE, APPROVE_EXPENSE, PAY_EXPENSE, VIEW_REPORTS,
)
from .permissions import ActionDjangoModelPermissions
from ..services import ExpenseService, ReportService, AvanceService
from .serializers import (
    ExpenseListSerializer,
    ExpenseDetailSerializer,
    ExpenseWriteSerializer,
    ExpenseCategorySerializer,
    ExpenseCategoryTreeSerializer,
    CostCenterSerializer,
    ExpenseApprovalSerializer,
    ExpensePaymentSerializer,
    ExpenseCommentSerializer,
    BudgetDepenseSerializer,
    AvanceDepenseSerializer,
    JustificationAvanceSerializer,
)


def _contexte_entreprise(request):
    return resoudre_entreprise(
        request,
        required=EXPENSES["ENABLE_MULTI_ENTREPRISE"],
    )


def _scope_entreprise(queryset, request, *, prefix="", include_global=False):
    contexte = _contexte_entreprise(request)
    return filtrer_par_entreprise(
        queryset,
        contexte,
        prefix=prefix,
        include_global=include_global,
    )


def _entreprise_kwargs(request):
    contexte = _contexte_entreprise(request)
    return contexte.as_kwargs() if contexte else {}


def _api_error(exc):
    if isinstance(exc, PermissionDenied):
        return Response({"error": str(exc)}, status=status.HTTP_403_FORBIDDEN)
    if isinstance(exc, DjangoValidationError):
        payload = getattr(exc, "message_dict", None) or getattr(exc, "messages", None) or str(exc)
        return Response({"error": payload}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class ExpenseViewSet(viewsets.ModelViewSet):
    permission_classes = [ActionDjangoModelPermissions]
    action_permission_map = {
        "submit": CHANGE_EXPENSE,
        "request_approval": CHANGE_EXPENSE,
        "approve": APPROVE_EXPENSE,
        "reject": APPROVE_EXPENSE,
        "pay": PAY_EXPENSE,
        "cancel": CHANGE_EXPENSE,
        "archive": CHANGE_EXPENSE,
        "attachment": CHANGE_EXPENSE,
        "report": VIEW_REPORTS,
        "export": VIEW_REPORTS,
    }
    filterset_fields = [
        "status", "category", "expense_nature", "cost_center", "currency", "user",
        "projet_source", "projet_reference",
    ]
    search_fields = [
        "reference_number", "description", "vendor",
        "projet_reference", "projet_libelle",
    ]

    def get_queryset(self):
        qs = Expense.objects.filter(supprime_le__isnull=True).select_related(
            "user", "category", "cost_center", "approved_by"
        ).prefetch_related("attachments", "approvals", "payments", "comments")
        qs = _scope_entreprise(qs, self.request)
        return HookRegistry.filter_queryset(qs, user=self.request.user, request=self.request)

    def get_serializer_class(self):
        if self.action == "list":
            return ExpenseListSerializer
        if self.action in ("create", "update", "partial_update"):
            return ExpenseWriteSerializer
        return ExpenseDetailSerializer

    def get_queryset(self):
        return _scope_entreprise(
            super().get_queryset(),
            self.request,
            prefix="expense__",
        )

    def create(self, request, *args, **kwargs):
        serializer = ExpenseWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            depense = ExpenseService.create(
                {
                    **serializer.validated_data,
                    **_entreprise_kwargs(request),
                    "user": request.user,
                },
                user=request.user,
            )
        except (WorkflowError, DjangoValidationError, PermissionDenied) as exc:
            return _api_error(exc)
        return Response(ExpenseDetailSerializer(depense).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        depense = self.get_object()
        serializer = ExpenseWriteSerializer(depense, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        try:
            depense = ExpenseService.update(depense, serializer.validated_data, user=request.user)
        except (WorkflowError, DjangoValidationError, PermissionDenied) as exc:
            return _api_error(exc)
        return Response(ExpenseDetailSerializer(depense).data)

    def destroy(self, request, *args, **kwargs):
        depense = self.get_object()
        try:
            ExpenseService.delete(depense, user=request.user)
        except (WorkflowError, DjangoValidationError, PermissionDenied) as exc:
            return _api_error(exc)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _transition(self, request, method, **kwargs):
        try:
            depense = self.get_object()
            result = method(depense, user=request.user, **kwargs)
            return Response(ExpenseDetailSerializer(result).data)
        except (WorkflowError, DjangoValidationError, PermissionDenied) as exc:
            return _api_error(exc)

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        return self._transition(request, ExpenseService.submit)

    @action(detail=True, methods=["post"])
    def request_approval(self, request, pk=None):
        return self._transition(request, ExpenseService.request_approval)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        return self._transition(request, ExpenseService.approve, comment=request.data.get("comment", ""))

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        return self._transition(request, ExpenseService.reject, reason=request.data.get("reason", ""))

    @action(detail=True, methods=["post"])
    def pay(self, request, pk=None):
        return self._transition(request, ExpenseService.pay, payment_data=request.data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        return self._transition(request, ExpenseService.cancel)

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        return self._transition(request, ExpenseService.archive)

    @action(detail=True, methods=["post"], parser_classes=[MultiPartParser, FormParser])
    def attachment(self, request, pk=None):
        depense = self.get_object()
        fichier = request.FILES.get("file")
        if not fichier:
            raise ValidationError({"file": "Fichier obligatoire."})
        try:
            piece = ExpenseService.add_attachment(
                depense, fichier, request.data.get("filename") or fichier.name, user=request.user
            )
        except DjangoValidationError as exc:
            return _api_error(exc)
        return Response({"id": piece.pk, "filename": piece.filename}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"])
    def report(self, request):
        if not request.user.has_perm(VIEW_REPORTS):
            return Response({"error": f"Missing permission: {VIEW_REPORTS}"}, status=status.HTTP_403_FORBIDDEN)
        start = request.query_params.get("start", str(date.today().replace(day=1)))
        end = request.query_params.get("end", str(date.today()))
        try:
            start_date = datetime.strptime(start, "%Y-%m-%d").date()
            end_date = datetime.strptime(end, "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Dates attendues au format YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)
        report = ReportService.generate_report(
            start_date,
            end_date,
            request.query_params.get("cost_center"),
            queryset=self.get_queryset(),
        )
        return Response(report)

    @action(detail=False, methods=["get"])
    def export(self, request):
        if not request.user.has_perm(VIEW_REPORTS):
            return Response({"error": f"Missing permission: {VIEW_REPORTS}"}, status=status.HTTP_403_FORBIDDEN)
        return ReportService.export_csv(self.filter_queryset(self.get_queryset()))


class ExpenseCategoryViewSet(viewsets.ModelViewSet):
    queryset = ExpenseCategory.objects.all()
    permission_classes = [ActionDjangoModelPermissions]
    filterset_fields = [
        "expense_nature", "is_active", "entreprise_source", "entreprise_reference"
    ]
    search_fields = ["code", "name", "default_account_code"]

    def get_serializer_class(self):
        return ExpenseCategoryTreeSerializer if self.request.query_params.get("tree") else ExpenseCategorySerializer

    def get_queryset(self):
        qs = ExpenseCategory.objects.select_related("parent")
        qs = _scope_entreprise(
            qs,
            self.request,
            include_global=EXPENSES["ALLOW_GLOBAL_CATEGORIES"],
        )
        if self.request.query_params.get("roots"):
            qs = qs.filter(parent__isnull=True)
        return qs

    def perform_create(self, serializer):
        serializer.save(**_entreprise_kwargs(self.request))

    def perform_update(self, serializer):
        obj = self.get_object()
        if (
            EXPENSES["ENABLE_MULTI_ENTREPRISE"]
            and getattr(obj, "est_globale", False)
            and not (
                self.request.user.is_superuser
                and EXPENSES["MULTI_ENTREPRISE_SUPERUSER_GLOBAL"]
            )
        ):
            raise PermissionDenied(
                "Les catégories globales sont en lecture seule dans ce contexte."
            )
        serializer.save()

    def perform_destroy(self, instance):
        if (
            EXPENSES["ENABLE_MULTI_ENTREPRISE"]
            and getattr(instance, "est_globale", False)
            and not (
                self.request.user.is_superuser
                and EXPENSES["MULTI_ENTREPRISE_SUPERUSER_GLOBAL"]
            )
        ):
            raise PermissionDenied(
                "Les catégories globales sont en lecture seule dans ce contexte."
            )
        instance.delete()


class CostCenterViewSet(viewsets.ModelViewSet):
    queryset = CostCenter.objects.all()
    serializer_class = CostCenterSerializer
    permission_classes = [ActionDjangoModelPermissions]
    filterset_fields = ["entreprise_source", "entreprise_reference", "is_active"]
    search_fields = ["code", "name"]

    def get_queryset(self):
        return _scope_entreprise(
            super().get_queryset(),
            self.request,
        )

    def perform_create(self, serializer):
        serializer.save(**_entreprise_kwargs(self.request))


class ExpensePaymentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ExpensePayment.objects.select_related("expense", "paid_by").all()
    serializer_class = ExpensePaymentSerializer
    filterset_fields = ["payment_method", "expense", "compte_reference"]
    permission_classes = [ActionDjangoModelPermissions]

    def get_queryset(self):
        return _scope_entreprise(
            super().get_queryset(),
            self.request,
            prefix="expense__",
        )


class ExpenseApprovalViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ExpenseApproval.objects.select_related("expense", "approved_by").all()
    serializer_class = ExpenseApprovalSerializer
    filterset_fields = ["decision", "expense"]
    permission_classes = [ActionDjangoModelPermissions]

    def get_queryset(self):
        return _scope_entreprise(
            super().get_queryset(),
            self.request,
            prefix="expense__",
        )


class ExpenseCommentViewSet(viewsets.ModelViewSet):
    queryset = ExpenseComment.objects.select_related("expense", "user").all()
    serializer_class = ExpenseCommentSerializer
    permission_classes = [ActionDjangoModelPermissions]
    action_permission_map = {"create": CHANGE_EXPENSE}
    http_method_names = ["get", "post", "head", "options"]

    def create(self, request, *args, **kwargs):
        serializer = ExpenseCommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            contexte = _contexte_entreprise(request)
            verifier_appartenance(
                data["expense"],
                contexte,
                label="Dépense",
            )
            commentaire = ExpenseService.add_comment(
                data["expense"], data["comment"], user=request.user
            )
        except (DjangoValidationError, PermissionDenied) as exc:
            return _api_error(exc)
        return Response(
            ExpenseCommentSerializer(commentaire).data,
            status=status.HTTP_201_CREATED,
        )


class BudgetDepenseViewSet(viewsets.ModelViewSet):
    queryset = BudgetDepense.objects.select_related("categorie", "centre_cout").all()
    serializer_class = BudgetDepenseSerializer
    permission_classes = [ActionDjangoModelPermissions]
    filterset_fields = [
        "actif", "bloquant", "categorie", "centre_cout",
        "projet_source", "projet_reference",
    ]
    search_fields = ["nom", "projet_reference", "projet_libelle"]

    def get_queryset(self):
        qs = _scope_entreprise(super().get_queryset(), self.request)
        return HookRegistry.filter_queryset(qs, user=self.request.user, request=self.request)

    def perform_create(self, serializer):
        serializer.save(**_entreprise_kwargs(self.request))


class AvanceDepenseViewSet(viewsets.ModelViewSet):
    action_permission_map = {
        "justifier": "django_expenses.change_avancedepense",
        "solder": "django_expenses.change_avancedepense",
    }
    queryset = AvanceDepense.objects.select_related("beneficiaire", "cree_par").prefetch_related("justifications")
    serializer_class = AvanceDepenseSerializer
    permission_classes = [ActionDjangoModelPermissions]
    filterset_fields = [
        "statut", "beneficiaire", "compte_reference",
        "entreprise_source", "entreprise_reference",
    ]
    search_fields = ["reference", "objet"]

    def get_queryset(self):
        qs = _scope_entreprise(super().get_queryset(), self.request)
        return HookRegistry.filter_queryset(qs, user=self.request.user, request=self.request)

    def create(self, request, *args, **kwargs):
        serializer = AvanceDepenseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            entreprise = _entreprise_kwargs(request)
            avance = AvanceService.creer(
                beneficiaire=data["beneficiaire"],
                montant_accorde=data["montant_accorde"],
                date_avance=data["date_avance"],
                objet=data["objet"],
                reference=data["reference"],
                cree_par=request.user,
                compte_reference=data.get("compte_reference", ""),
                notes=data.get("notes", ""),
                **entreprise,
            )
        except DjangoValidationError as exc:
            return _api_error(exc)
        return Response(AvanceDepenseSerializer(avance).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], parser_classes=[MultiPartParser, FormParser])
    def justifier(self, request, pk=None):
        avance = self.get_object()
        serializer = JustificationAvanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            justification = AvanceService.ajouter_justification(
                avance,
                montant=data["montant"],
                date_depense=data["date_depense"],
                description=data["description"],
                depense=data.get("depense"),
                piece=data.get("piece"),
                user=request.user,
            )
        except DjangoValidationError as exc:
            return _api_error(exc)
        return Response(JustificationAvanceSerializer(justification).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def solder(self, request, pk=None):
        try:
            avance = AvanceService.solder(self.get_object(), user=request.user)
        except DjangoValidationError as exc:
            return _api_error(exc)
        return Response(AvanceDepenseSerializer(avance).data)
