from django.shortcuts import render
from django.db.models import Q
from .models import FIR, ActionLog

def all_reports(request):
    firs = FIR.objects.all().order_by('-date_reported', '-created_at')
    system_alerts = ActionLog.objects.filter(action__contains="SYSTEM ALERT").order_by('-timestamp')[:5]

    query = request.GET.get('q')
    status_filter = request.GET.get('status')

    if query:
        firs = firs.filter(
            Q(case_id__icontains=query) |
            Q(title__icontains=query) |
            Q(suspects__name__icontains=query) |
            Q(suspects__cnic__icontains=query)
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