from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import FIR, ActionLog

@receiver(post_save, sender=FIR)
def log_fir_save(sender, instance, created, **kwargs):
    action_type = "New FIR Registered" if created else "FIR Updated"
    # Use fir_no
    ActionLog.objects.create(action=f"{action_type}: {instance.fir_no} (Status: {instance.get_status_display()})")

@receiver(post_delete, sender=FIR)
def log_fir_delete(sender, instance, **kwargs):
    # Use fir_no
    ActionLog.objects.create(action=f"FIR DELETED: {instance.fir_no}")