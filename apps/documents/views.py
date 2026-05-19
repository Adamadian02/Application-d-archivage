from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import FileResponse
from .models import Document
from .forms import DocumentForm
from apps.historique.models import Historique
from apps.categories.models import Categorie

@login_required
def liste_documents(request):
    docs = Document.objects.exclude(statut='supprime')
    if request.user.is_archiviste():
        docs = docs.filter(archiviste=request.user)
    query = request.GET.get('q', '')
    cat_filter = request.GET.get('categorie', '')
    conf_filter = request.GET.get('confidentialite', '')
    statut_filter = request.GET.get('statut', '')
    if query:
        docs = docs.filter(Q(titre__icontains=query) | Q(description__icontains=query) | Q(tags__nom__icontains=query)).distinct()
    if cat_filter:
        docs = docs.filter(categorie__id=cat_filter)
    if conf_filter:
        docs = docs.filter(confidentialite=conf_filter)
    if statut_filter:
        docs = docs.filter(statut=statut_filter)
    categories = Categorie.objects.all()
    return render(request, 'archiviste/documents.html', {
        'documents': docs, 'query': query, 'categories': categories,
        'cat_filter': cat_filter, 'conf_filter': conf_filter
    })

@login_required
def upload_document(request):
    form = DocumentForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        doc = form.save(commit=False)
        doc.archiviste = request.user
        doc.save()
        form.save()
        Historique.objects.create(utilisateur=request.user, action='upload', description=f'Upload du document "{doc.titre}"')
        messages.success(request, f'Document "{doc.titre}" uploadé avec succès.')
        return redirect('liste_documents')
    return render(request, 'archiviste/upload.html', {'form': form})

@login_required
def modifier_document(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    if request.user.is_archiviste() and doc.archiviste != request.user:
        messages.error(request, "Vous n'avez pas la permission de modifier ce document.")
        return redirect('liste_documents')
    form = DocumentForm(request.POST or None, request.FILES or None, instance=doc)
    if request.method == 'POST' and form.is_valid():
        form.save()
        Historique.objects.create(utilisateur=request.user, action='modification', description=f'Modification du document "{doc.titre}"')
        messages.success(request, 'Document modifié avec succès.')
        return redirect('liste_documents')
    return render(request, 'archiviste/document_form.html', {'form': form, 'document': doc})

@login_required
def archiver_document(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    doc.statut = 'archive'
    doc.save()
    Historique.objects.create(utilisateur=request.user, action='archivage', description=f'Archivage du document "{doc.titre}"')
    messages.success(request, 'Document archivé.')
    return redirect('liste_documents')

@login_required
def supprimer_document(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    if request.method == 'POST':
        titre = doc.titre
        doc.statut = 'supprime'
        doc.save()
        Historique.objects.create(utilisateur=request.user, action='suppression', description=f'Suppression du document "{titre}"')
        messages.success(request, 'Document supprimé.')
        return redirect('liste_documents')
    return render(request, 'archiviste/document_confirm_delete.html', {'document': doc})

@login_required
def detail_document(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    return render(request, 'archiviste/document_detail.html', {'document': doc})

@login_required
def telecharger_document(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    Historique.objects.create(utilisateur=request.user, action='telechargement', description=f'Téléchargement du document "{doc.titre}"')
    response = FileResponse(doc.fichier.open('rb'), as_attachment=True, filename=doc.fichier.name.split('/')[-1])
    return response

@login_required
def recherche_documents(request):
    query = request.GET.get('q', '')
    cat_filter = request.GET.get('categorie', '')
    conf_filter = request.GET.get('confidentialite', '')
    date_debut = request.GET.get('date_debut', '')
    date_fin = request.GET.get('date_fin', '')
    docs = Document.objects.exclude(statut='supprime')
    if query:
        docs = docs.filter(Q(titre__icontains=query) | Q(description__icontains=query) | Q(tags__nom__icontains=query) | Q(archiviste__username__icontains=query)).distinct()
    if cat_filter:
        docs = docs.filter(categorie__id=cat_filter)
    if conf_filter:
        docs = docs.filter(confidentialite=conf_filter)
    if date_debut:
        docs = docs.filter(created_at__date__gte=date_debut)
    if date_fin:
        docs = docs.filter(created_at__date__lte=date_fin)
    categories = Categorie.objects.all()
    template = 'admin_ged/recherche.html' if request.user.is_admin() else 'archiviste/recherche.html'
    return render(request, template, {
        'documents': docs, 'query': query, 'categories': categories,
        'cat_filter': cat_filter, 'conf_filter': conf_filter,
        'date_debut': date_debut, 'date_fin': date_fin
    })

@login_required
def consultation_archives(request):
    if not request.user.is_admin():
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    docs = Document.objects.all()
    return render(request, 'admin_ged/archives.html', {'documents': docs})
