from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import FIR
from datetime import timedelta

class Command(BaseCommand):
    help = 'Update FIR status based on 14-day inactivity'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        firs = FIR.objects.exclude(status__in=['SOLVED', 'EXPIRED'])

        for fir in firs:
            # Kitne din guzar gaye?
            days_inactive = (now - fir.last_updated).days
            
            # Logic: 14 se 17 din (Snooze Period)
            if 14 <= days_inactive < 17 and fir.status != 'SNOOZED':
                fir.status = 'SNOOZED'
                fir.save()
                self.stdout.write(self.style.WARNING(f"Snoozed: {fir.case_id}"))

            # Logic: 17 din se zyada (Expire)
            elif days_inactive >= 17:
                fir.status = 'EXPIRED'
                fir.save()
                self.stdout.write(self.style.ERROR(f"Expired: {fir.case_id}"))