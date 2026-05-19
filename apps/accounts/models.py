from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('administrateur', 'Administrateur'),
        ('archiviste', 'Archiviste'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='archiviste')
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True)
    departement = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_admin(self):
        return self.role == 'administrateur'

    def is_archiviste(self):
        return self.role == 'archiviste'

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
