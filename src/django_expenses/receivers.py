from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .models import Expense
from .settings import EXPENSES


@receiver(pre_save, sender=Expense, dispatch_uid="expense_auto_reference")
def expense_auto_reference(sender, instance, **kwargs):
    """Reserve a temporary unique reference before the initial INSERT."""
    if not instance.reference_number:
        if instance.pk:
            instance.reference_number = generate_reference(instance)
        else:
            instance.reference_number = f"TMP-{id(instance):x}"


@receiver(post_save, sender=Expense, dispatch_uid="expense_finalize_reference")
def expense_finalize_reference(sender, instance, created, **kwargs):
    """Finalize the stable reference after a primary key exists.

    Business signals deliberately live in ExpenseService only. Keeping them out of
    model signals prevents duplicate accounting/cash side effects.
    """
    if created and instance.reference_number.startswith("TMP-"):
        instance.reference_number = generate_reference(instance)
        Expense.objects.filter(pk=instance.pk).update(reference_number=instance.reference_number)


def generate_reference(instance):
    prefix = EXPENSES["AUTO_REFERENCE_PREFIX"]
    creation_date = instance.created_at
    return f"{prefix}-{creation_date:%Y%m}-{instance.pk:06d}"
