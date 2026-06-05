from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Historique

@login_required
def historique_systeme(request):
    if not request.user.is_admin():
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    logs = Historique.objects.select_related('utilisateur').all()
    action_filter = request.GET.get('action', '')
    if action_filter:
        logs = logs.filter(action=action_filter)
    # Notifications réelles pour la navbar (base.html)
    notifications = Historique.objects.select_related('utilisateur').order_by('-created_at')[:5]
    
    return render(request, 'admin_ged/historique.html', {
        'logs': logs, 'action_filter': action_filter,
        'action_choices': Historique.ACTION_CHOICES,
        'notifications': notifications
    })

@login_required
def historique_personnel(request):
    logs = Historique.objects.filter(utilisateur=request.user)
    return render(request, 'archiviste/historique.html', {'logs': logs})
