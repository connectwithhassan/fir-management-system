from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import FIR, ActionLog

class Command(BaseCommand):
    help = 'Updates FIR status based on 14-day (Interim) and 17-day (Expired) rules'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        # Exclude statuses that shouldn't be auto-updated
        firs = FIR.objects.exclude(status__in=['SOLVED', 'EXPIRED', 'CHALLAN', 'FINAL_REPORT', 'A_CLASS'])
        count = 0

        for fir in firs:
            days_passed = (today - fir.date_reported).days
            
            # Logic 1: 14 Days -> INTERIM (Will blink on frontend)
            if days_passed == 14 and fir.status != 'INTERIM':
                fir.status = 'INTERIM'
                fir.save()
                ActionLog.objects.create(user=None, action=f"⚠️ SYSTEM ALERT: FIR {fir.fir_no} status changed to INTERIM (14 Days Passed)")
                count += 1

            # Logic 2: 17 Days -> EXPIRED
            elif days_passed >= 17:
                fir.status = 'EXPIRED'
                fir.save()
                ActionLog.objects.create(user=None, action=f"⛔ SYSTEM ALERT: FIR {fir.fir_no} status changed to EXPIRED (17 Days Limit Reached)")
                count += 1
        
        self.stdout.write(f"Check Complete. {count} updates made.")