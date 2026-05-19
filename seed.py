"""
Script de peuplement de la base de données avec des données de démonstration.
Usage: python manage.py shell < seed.py
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ged_universitaire.settings')
django.setup()

from apps.accounts.models import User
from apps.categories.models import Categorie
from apps.documents.models import Document, Tag
from apps.historique.models import Historique

print("Création des utilisateurs...")
admin = User.objects.create_superuser(
    username='admin', password='admin123',
    first_name='Directeur', last_name='Faculté',
    email='admin@universite.gn', role='administrateur'
)
archiviste = User.objects.filter(username='archiviste').first()
if not archiviste:
    archiviste = User.objects.create_user(
        username='archiviste', password='archiviste123',
        first_name='Marie', last_name='Camara',
        email='marie@universite.gn', role='archiviste',
        departement='Secrétariat Central', telephone='+224 620 000 001'
    )

print("Création des catégories...")
cats = [
    ('Administratif', 'Documents administratifs', 'primary'),
    ('Académique', 'Documents académiques et pédagogiques', 'success'),
    ('Financier', 'Documents financiers et comptables', 'warning'),
    ('RH', 'Ressources humaines et personnel', 'info'),
    ('Juridique', 'Documents juridiques et réglementaires', 'danger'),
]
for nom, desc, couleur in cats:
    Categorie.objects.get_or_create(nom=nom, defaults={'description': desc, 'couleur': couleur})

print("Création des tags...")
tag_names = ['urgent', 'archivé', 'confidentiel', 'rapport', '2024', 'officiel']
for t in tag_names:
    Tag.objects.get_or_create(nom=t)

print("Création de l'historique...")
actions = [
    ('connexion', 'Connexion au système'),
    ('upload', 'Upload du document "Rapport annuel 2024"'),
    ('modification', 'Modification du document "Budget 2024"'),
    ('creation_utilisateur', 'Création du compte marie.camara'),
]
for action, desc in actions:
    Historique.objects.create(utilisateur=admin, action=action, description=desc)

print("✅ Données de démonstration créées avec succès!")
print("\nComptes de connexion:")
print("  Admin: username=admin | password=admin123")
print("  Archiviste: username=archiviste | password=archiviste123")
