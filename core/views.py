from django.shortcuts import render
from django.db.models import Q
from .models import FIR, ActionLog

def all_reports(request):
    # 1. Get FIRs
    firs = FIR.objects.all().order_by('-date_reported', '-created_at')
    
    # 2. Get System Alerts
    system_alerts = ActionLog.objects.filter(action__contains="SYSTEM ALERT").order_by('-timestamp')[:5]

    # 3. Filter Logic
    query = request.GET.get('q')
    status_filter = request.GET.get('status')

    if query:
        firs = firs.filter(
            Q(fir_no__icontains=query) | # Changed from case_id
            Q(title__icontains=query) |
            Q(accuseds__name__icontains=query) | # Changed from suspects
            Q(accuseds__cnic__icontains=query)   # Changed from suspects
        ).distinct()

    if status_filter and status_filter != 'ALL':
        firs = firs.filter(status=status_filter)

    context = {
        'firs': firs,
        'system_alerts': system_alerts,
        'current_query': query if query else '',
        'current_status': status_filter if status_filter else 'ALL'
    }
    return render(request, 'all_reports.html', context)