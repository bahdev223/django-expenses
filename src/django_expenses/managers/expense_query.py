from django.db import models
from django.db.models import Sum, F, Count
from django.db.models.functions import TruncMonth
from django.utils import timezone


class ExpenseQuerySet(models.QuerySet):
    def by_status(self, status):
        return self.filter(status=status)

    def by_user(self, user):
        return self.filter(user=user)

    def by_period(self, start_date, end_date):
        return self.filter(
            date_incurred__gte=start_date, date_incurred__lte=end_date
        )

    def by_cost_center(self, cost_center):
        return self.filter(cost_center=cost_center)

    def pending_approval(self):
        return self.filter(status="pending_approval")

    def approved(self):
        return self.filter(status="approved")

    def paid(self):
        return self.filter(status="paid")

    def draft(self):
        return self.filter(status="draft")

    def rejected(self):
        return self.filter(status="rejected")

    def editable(self):
        return self.filter(status__in=["draft", "rejected"])

    def total_amount(self):
        return self.aggregate(total=Sum(F("amount") + F("tax_amount")))["total"] or 0

    def total_by_category(self):
        return (
            self.values("expense_type__category__name")
            .annotate(total=Sum(F("amount") + F("tax_amount")))
            .order_by("-total")
        )

    def total_by_cost_center(self):
        return (
            self.values("cost_center__code", "cost_center__name")
            .annotate(total=Sum(F("amount") + F("tax_amount")))
            .order_by("-total")
        )

    def monthly_summary(self, year=None):
        if year is None:
            year = timezone.now().year
        return (
            self.filter(date_incurred__year=year)
            .annotate(month=TruncMonth("date_incurred"))
            .values("month")
            .annotate(
                total=Sum(F("amount") + F("tax_amount")),
                count=Count("id"),
            )
            .order_by("month")
        )
