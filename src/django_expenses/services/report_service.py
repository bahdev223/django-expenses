from django.http import HttpResponse
import csv

from ..models import Expense


class ReportService:
    @staticmethod
    def generate_report(start_date, end_date, cost_center=None):
        qs = Expense.objects.filter(
            date_incurred__gte=start_date, date_incurred__lte=end_date
        )
        if cost_center:
            qs = qs.filter(cost_center=cost_center)
        return {
            "total_expenses": qs.total_amount(),
            "count": qs.count(),
            "by_category": list(qs.total_by_category()),
            "by_status": {
                label: qs.filter(status=code).count()
                for code, label in Expense.Status.choices
            },
            "by_cost_center": list(qs.total_by_cost_center()),
            "monthly": list(qs.monthly_summary()),
            "start_date": start_date,
            "end_date": end_date,
        }

    @staticmethod
    def export_csv(queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=expenses.csv"
        writer = csv.writer(response)
        writer.writerow([
            "Reference", "Date", "Amount", "Currency", "Status",
            "Category", "Type", "Cost Center", "Vendor", "Description",
        ])
        for e in queryset.select_related(
            "expense_type__category", "cost_center"
        ):
            writer.writerow([
                e.reference_number,
                e.date_incurred,
                e.total_amount,
                e.currency,
                e.get_status_display(),
                e.expense_type.category.name if e.expense_type else "",
                e.expense_type.name if e.expense_type else "",
                e.cost_center.name if e.cost_center else "",
                e.vendor,
                e.description[:100],
            ])
        return response
