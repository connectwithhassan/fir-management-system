from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import FIR, ActionLog

class Command(BaseCommand):
    help = 'Updates FIR status and logs alerts to database'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        firs = FIR.objects.exclude(status__in=['SOLVED', 'EXPIRED'])
        count = 0

        for fir in firs:
            days_passed = (today - fir.date_reported).days
            
            # 14 Days Logic
            if days_passed == 14 and fir.status != 'SNOOZED':
                fir.status = 'SNOOZED'
                fir.save()
                ActionLog.objects.create(user=None, action=f"⚠️ SYSTEM ALERT: FIR {fir.case_id} SNOOZED (14 Days Inactive)")
                count += 1

            # 17 Days Logic
            elif days_passed >= 17:
                fir.status = 'EXPIRED'
                fir.save()
                ActionLog.objects.create(user=None, action=f"⛔ SYSTEM ALERT: FIR {fir.case_id} EXPIRED (17 Days Limit)")
                count += 1
        
        self.stdout.write(f"Check Complete. {count} updates made.")