import json
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.db.models.functions import TruncMonth
from .models import User
from .forms import ConnexionForm, UserCreateForm, UserEditForm, ProfilForm
from apps.documents.models import Document
from apps.historique.models import Historique

def connexion(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = ConnexionForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        ip = request.META.get('REMOTE_ADDR')
        Historique.objects.create(utilisateur=user, action='connexion', description='Connexion au système', ip_address=ip)
        return redirect('dashboard')
    return render(request, 'auth/login.html', {'form': form})

def deconnexion(request):
    if request.user.is_authenticated:
        Historique.objects.create(utilisateur=request.user, action='deconnexion', description='Déconnexion du système')
    logout(request)
    return redirect('connexion')

@login_required
def dashboard(request):
    user = request.user
    if user.is_admin():
        docs = Document.objects.all()
        users = User.objects.all()
        recent_docs = docs.order_by('-created_at')[:5]
        recent_activity = Historique.objects.select_related('utilisateur').all().order_by('-created_at')[:10]

        today = datetime.date.today()
        stats = {
            'total_docs': docs.count(),
            'total_users': users.count(),
            'docs_ce_mois': docs.filter(created_at__month=today.month, created_at__year=today.year).count(),
            'archivistes': users.filter(role='archiviste').count(),
        }

        # Graphique réel : documents par mois sur 6 mois
        mois_labels = []
        mois_data = []
        mois_fr = ['Janvier','Février','Mars','Avril','Mai','Juin','Juillet','Août','Septembre','Octobre','Novembre','Décembre']
        for i in range(5, -1, -1):
            m = today.month - i
            y = today.year
            while m <= 0:
                m += 12
                y -= 1
            count = docs.filter(created_at__month=m, created_at__year=y).count()
            mois_labels.append(mois_fr[m - 1])
            mois_data.append(count)

        # Répartition par confidentialité (données réelles)
        conf_data = {
            'public': docs.filter(confidentialite='public').count(),
            'interne': docs.filter(confidentialite='interne').count(),
            'confidentiel': docs.filter(confidentialite='confidentiel').count(),
            'secret': docs.filter(confidentialite='secret').count(),
        }
        total_conf = sum(conf_data.values())
        if total_conf > 0:
            conf_pct = {k: round(v * 100 / total_conf) for k, v in conf_data.items()}
        else:
            conf_pct = {'public': 0, 'interne': 0, 'confidentiel': 0, 'secret': 0}

        # Notifications réelles (dernières activités)
        notifications = Historique.objects.select_related('utilisateur').order_by('-created_at')[:5]

        return render(request, 'admin_ged/dashboard.html', {
            'stats': stats,
            'recent_docs': recent_docs,
            'recent_activity': recent_activity,
            'mois_labels': mois_labels,
            'mois_data': mois_data,
            'conf_pct': conf_pct,
            'notifications': notifications,
        })
    else:
        docs = Document.objects.filter(archiviste=user)
        recent_docs = docs.order_by('-created_at')[:5]
        recent_activity = Historique.objects.filter(utilisateur=user).order_by('-created_at')[:8]
        today = datetime.date.today()
        from apps.categories.models import Categorie
        stats = {
            'mes_docs': docs.count(),
            'docs_ce_mois': docs.filter(created_at__month=today.month, created_at__year=today.year).count(),
            'categories': Categorie.objects.count(),
        }
        notifications = Historique.objects.filter(utilisateur=user).order_by('-created_at')[:5]
        return render(request, 'archiviste/dashboard.html', {
            'stats': stats,
            'recent_docs': recent_docs,
            'recent_activity': recent_activity,
            'notifications': notifications,
        })

@login_required
def gestion_utilisateurs(request):
    query = request.GET.get('q', '')
    users = User.objects.all()
    if query:
        users = users.filter(Q(username__icontains=query)|Q(first_name__icontains=query)|Q(last_name__icontains=query)|Q(email__icontains=query))
    return render(request, 'archiviste/utilisateurs.html', {'users': users, 'query': query})

@login_required
def creer_utilisateur(request):
    form = UserCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        Historique.objects.create(utilisateur=request.user, action='creation_utilisateur', description=f'Création du compte {user.username}')
        messages.success(request, f'Utilisateur {user.get_full_name()} créé avec succès.')
        return redirect('gestion_utilisateurs')
    return render(request, 'archiviste/utilisateur_form.html', {'form': form, 'titre': 'Créer un utilisateur'})

@login_required
def modifier_utilisateur(request, pk):
    user = get_object_or_404(User, pk=pk)
    form = UserEditForm(request.POST or None, instance=user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        Historique.objects.create(utilisateur=request.user, action='modification_utilisateur', description=f'Modification du compte {user.username}')
        messages.success(request, 'Utilisateur modifié avec succès.')
        return redirect('gestion_utilisateurs')
    return render(request, 'archiviste/utilisateur_form.html', {'form': form, 'titre': "Modifier l'utilisateur", 'user_edit': user})

@login_required
def supprimer_utilisateur(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        username = user.username
        user.delete()
        Historique.objects.create(utilisateur=request.user, action='suppression_utilisateur', description=f'Suppression du compte {username}')
        messages.success(request, 'Utilisateur supprimé.')
        return redirect('gestion_utilisateurs')
    return render(request, 'archiviste/utilisateur_confirm_delete.html', {'user_del': user})

@login_required
def profil(request):
    form = ProfilForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profil mis à jour avec succès.')
        return redirect('profil')
    historique = Historique.objects.filter(utilisateur=request.user).order_by('-created_at')[:10]
    return render(request, 'partials/profil.html', {'form': form, 'historique': historique})

def mot_de_passe_oublie(request):
    return render(request, 'auth/forgot_password.html')

def error_403(request, exception=None):
    return render(request, 'errors/403.html', status=403)

def error_404(request, exception=None):
    return render(request, 'errors/404.html', status=404)