from django.db import models
from django.utils.translation import gettext_lazy as _


class ExpenseAttachment(models.Model):
    expense = models.ForeignKey(
        "Expense",
        on_delete=models.CASCADE,
        related_name="attachments",
    )
    file = models.FileField(upload_to="expenses/attachments/%Y/%m/")
    filename = models.CharField(max_length=500)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = _("Expense attachment")
        verbose_name_plural = _("Expense attachments")

    def __str__(self):
        return self.filename
