from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import FileResponse
from .models import Document
from .forms import DocumentForm
from apps.historique.models import Historique
from apps.categories.models import Categorie

from django.core.paginator import Paginator

@login_required
def liste_documents(request):
    docs = Document.objects.exclude(statut='supprime').order_by('-created_at')
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
    paginator = Paginator(docs, 20)
    page_number = request.GET.get('page')
    docs_page = paginator.get_page(page_number)
    
    categories = Categorie.objects.all()
    return render(request, 'archiviste/documents.html', {
        'documents': docs_page, 'query': query, 'categories': categories,
        'cat_filter': cat_filter, 'conf_filter': conf_filter, 'docs_count': paginator.count
    })

@login_required
def upload_document(request):
    form = DocumentForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        doc = form.save(commit=False)
        doc.archiviste = request.user
        doc.save()
        form.save_m2m()
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


def _check_document_access(user, doc):
    """
    Vérifie si l'utilisateur peut accéder au document.
    Retourne (can_access: bool, can_download: bool)

    Matrice :
      Admin / Archiviste propriétaire → accès total
      Autre archiviste :
        - confidentiel / secret  → refusé
        - interne                → lecture seule (pas de téléchargement)
        - public                 → accès total
    """
    if user.is_admin():
        return True, True
    if doc.archiviste == user:
        return True, True
    # Autre archiviste
    if doc.confidentialite in ('confidentiel', 'secret'):
        return False, False
    if doc.confidentialite == 'interne':
        return True, False   # peut voir, ne peut pas télécharger
    return True, True        # public


@login_required
def detail_document(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    can_access, can_download = _check_document_access(request.user, doc)
    if not can_access:
        messages.error(request, "Vous n'êtes pas autorisé à consulter ce document (niveau de confidentialité insuffisant).")
        return redirect('liste_documents')
    return render(request, 'archiviste/document_detail.html', {
        'document': doc,
        'can_download': can_download,
    })


@login_required
def telecharger_document(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    can_access, can_download = _check_document_access(request.user, doc)
    if not can_access or not can_download:
        messages.error(request, "Vous n'êtes pas autorisé à télécharger ce document.")
        return redirect('detail_document', pk=pk)
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
    # Les archivistes peuvent voir les documents publics/internes ou les leurs
    if request.user.is_archiviste():
        docs = docs.filter(Q(archiviste=request.user) | Q(confidentialite__in=['public', 'interne']))
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
        
    paginator = Paginator(docs, 20)
    page_number = request.GET.get('page')
    docs_page = paginator.get_page(page_number)
    
    categories = Categorie.objects.all()
    template = 'admin_ged/recherche.html' if request.user.is_admin() else 'archiviste/recherche.html'
    return render(request, template, {
        'documents': docs_page, 'query': query, 'categories': categories,
        'cat_filter': cat_filter, 'conf_filter': conf_filter,
        'date_debut': date_debut, 'date_fin': date_fin, 'docs_count': paginator.count
    })


@login_required
def consultation_archives(request):
    from collections import defaultdict
    # pyrefly: ignore [missing-import]
    from django.core.exceptions import PermissionDenied
    if not request.user.is_admin():
        raise PermissionDenied

    annee_filter = request.GET.get('annee', '')
    cat_filter   = request.GET.get('categorie', '')
    conf_filter  = request.GET.get('confidentialite', '')

    docs = Document.objects.filter(statut='archive').select_related('categorie', 'archiviste').order_by('-created_at')

    if annee_filter:
        docs = docs.filter(created_at__year=annee_filter)
    if cat_filter:
        docs = docs.filter(categorie__id=cat_filter)
    if conf_filter:
        docs = docs.filter(confidentialite=conf_filter)

    # Construction arborescence {année: {nom_catégorie: [documents]}}
    archives_par_annee = defaultdict(lambda: defaultdict(list))
    annees_disponibles = set()
    for doc in docs:
        annee = doc.created_at.year
        cat_nom = doc.categorie.nom if doc.categorie else 'Sans catégorie'
        archives_par_annee[annee][cat_nom].append(doc)
        annees_disponibles.add(annee)

    # Tri : années décroissantes, catégories alphabétiques
    archives_organisees = {
        annee: dict(sorted(cats.items()))
        for annee, cats in sorted(archives_par_annee.items(), reverse=True)
    }

    return render(request, 'admin_ged/archives.html', {
        'archives': archives_organisees,
        'annees': sorted(annees_disponibles, reverse=True),
        'categories': Categorie.objects.all(),
        'annee_filter': annee_filter,
        'cat_filter': cat_filter,
        'conf_filter': conf_filter,
        'total': docs.count(),
    })
