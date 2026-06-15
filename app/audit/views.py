from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from .models import AuditLog


def is_admin(user):
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(is_admin)
def audit_log_list_view(request):
    logs = AuditLog.objects.all().select_related('user').order_by('-created_at')[:200]
    action = request.GET.get('action')
    if action:
        logs = logs.filter(action__icontains=action)
    return render(request, 'audit/audit_log_list.html', {'logs': logs})
