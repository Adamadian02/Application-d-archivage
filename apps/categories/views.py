from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Categorie
from .forms import CategorieForm
from apps.historique.models import Historique

@login_required
def liste_categories(request):
    categories = Categorie.objects.filter(parent=None).prefetch_related('sous_categories')
    return render(request, 'archiviste/categories.html', {'categories': categories})

@login_required
def creer_categorie(request):
    form = CategorieForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        cat = form.save()
        Historique.objects.create(utilisateur=request.user, action='creation_categorie', description=f'Création de la catégorie {cat.nom}')
        messages.success(request, f'Catégorie "{cat.nom}" créée avec succès.')
        return redirect('liste_categories')
    return render(request, 'archiviste/categorie_form.html', {'form': form, 'titre': 'Créer une catégorie'})

@login_required
def modifier_categorie(request, pk):
    cat = get_object_or_404(Categorie, pk=pk)
    form = CategorieForm(request.POST or None, instance=cat)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Catégorie modifiée.')
        return redirect('liste_categories')
    return render(request, 'archiviste/categorie_form.html', {'form': form, 'titre': 'Modifier la catégorie', 'categorie': cat})

@login_required
def supprimer_categorie(request, pk):
    cat = get_object_or_404(Categorie, pk=pk)
    if request.method == 'POST':
        nom = cat.nom
        cat.delete()
        Historique.objects.create(utilisateur=request.user, action='suppression_categorie', description=f'Suppression de la catégorie {nom}')
        messages.success(request, 'Catégorie supprimée.')
        return redirect('liste_categories')
    return render(request, 'archiviste/categorie_confirm_delete.html', {'categorie': cat})
