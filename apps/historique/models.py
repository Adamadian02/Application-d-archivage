from django.db import models
from django.conf import settings

class Historique(models.Model):
    ACTION_CHOICES = [
        ('connexion', 'Connexion'),
        ('deconnexion', 'Déconnexion'),
        ('upload', 'Upload document'),
        ('modification', 'Modification'),
        ('suppression', 'Suppression'),
        ('archivage', 'Archivage'),
        ('telechargement', 'Téléchargement'),
        ('creation_utilisateur', 'Création utilisateur'),
        ('modification_utilisateur', 'Modification utilisateur'),
        ('suppression_utilisateur', 'Suppression utilisateur'),
        ('creation_categorie', 'Création catégorie'),
        ('suppression_categorie', 'Suppression catégorie'),
        ('autre', 'Autre'),
    ]
    ICON_MAP = {
        'connexion': 'bi-box-arrow-in-right',
        'deconnexion': 'bi-box-arrow-right',
        'upload': 'bi-cloud-upload',
        'modification': 'bi-pencil',
        'suppression': 'bi-trash',
        'archivage': 'bi-archive',
        'telechargement': 'bi-download',
        'creation_utilisateur': 'bi-person-plus',
        'modification_utilisateur': 'bi-person-gear',
        'suppression_utilisateur': 'bi-person-x',
        'creation_categorie': 'bi-folder-plus',
        'suppression_categorie': 'bi-folder-x',
        'autre': 'bi-info-circle',
    }
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_icon(self):
        return self.ICON_MAP.get(self.action, 'bi-info-circle')

    def __str__(self):
        return f"{self.utilisateur} - {self.action} - {self.created_at}"

    class Meta:
        verbose_name = 'Historique'
        ordering = ['-created_at']
