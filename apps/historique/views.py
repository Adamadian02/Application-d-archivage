from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Historique

@login_required
def historique_systeme(request):
    if not request.user.is_admin():
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    logs = Historique.objects.select_related('utilisateur').all().order_by('-created_at')
    action_filter = request.GET.get('action', '')
    if action_filter:
        logs = logs.filter(action=action_filter)
        
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    logs_page = paginator.get_page(page_number)
        
    return render(request, 'admin_ged/historique.html', {
        'logs': logs_page, 'action_filter': action_filter,
        'action_choices': Historique.ACTION_CHOICES, 'logs_count': paginator.count
    })

@login_required
def historique_personnel(request):
    logs = Historique.objects.filter(utilisateur=request.user).order_by('-created_at')
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    logs_page = paginator.get_page(page_number)
    return render(request, 'archiviste/historique.html', {'logs': logs_page, 'logs_count': paginator.count})
