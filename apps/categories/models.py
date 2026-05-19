from django.db import models

class Categorie(models.Model):
    COULEUR_CHOICES = [
        ('primary', 'Bleu'), ('success', 'Vert'), ('danger', 'Rouge'),
        ('warning', 'Orange'), ('info', 'Cyan'), ('secondary', 'Gris'),
        ('dark', 'Foncé'),
    ]
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    couleur = models.CharField(max_length=20, choices=COULEUR_CHOICES, default='primary')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='sous_categories')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = 'Catégorie'
        ordering = ['nom']
