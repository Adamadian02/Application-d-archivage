from django.db import models
from django.conf import settings
from apps.categories.models import Categorie
import os

class Tag(models.Model):
    nom = models.CharField(max_length=50, unique=True)
    def __str__(self): return self.nom

class Document(models.Model):
    CONFIDENTIALITE_CHOICES = [
        ('public', 'Public'),
        ('interne', 'Interne'),
        ('confidentiel', 'Confidentiel'),
        ('secret', 'Secret'),
    ]
    STATUT_CHOICES = [
        ('actif', 'Actif'),
        ('archive', 'Archivé'),
        ('supprime', 'Supprimé'),
    ]
    titre = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    fichier = models.FileField(upload_to='documents/%Y/%m/')
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    archiviste = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='documents')
    confidentialite = models.CharField(max_length=20, choices=CONFIDENTIALITE_CHOICES, default='interne')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='actif')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_extension(self):
        _, ext = os.path.splitext(self.fichier.name)
        return ext.lower()

    def get_icon(self):
        ext = self.get_extension()
        icons = {
            '.pdf': 'bi-file-earmark-pdf text-danger',
            '.doc': 'bi-file-earmark-word text-primary',
            '.docx': 'bi-file-earmark-word text-primary',
            '.xls': 'bi-file-earmark-excel text-success',
            '.xlsx': 'bi-file-earmark-excel text-success',
            '.png': 'bi-file-earmark-image text-warning',
            '.jpg': 'bi-file-earmark-image text-warning',
            '.jpeg': 'bi-file-earmark-image text-warning',
            '.ppt': 'bi-file-earmark-ppt text-orange',
            '.pptx': 'bi-file-earmark-ppt text-orange',
        }
        return icons.get(ext, 'bi-file-earmark text-secondary')

    def get_taille(self):
        try:
            size = self.fichier.size
            if size < 1024: return f"{size} B"
            elif size < 1024**2: return f"{size/1024:.1f} KB"
            else: return f"{size/1024**2:.1f} MB"
        except: return "N/A"

    def __str__(self): return self.titre

    class Meta:
        verbose_name = 'Document'
        ordering = ['-created_at']
