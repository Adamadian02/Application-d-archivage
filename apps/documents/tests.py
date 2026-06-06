# pyrefly: ignore [missing-import]
from django.test import TestCase, Client
# pyrefly: ignore [missing-import]
from django.urls import reverse
from apps.accounts.models import User
from apps.documents.models import Document
from apps.categories.models import Categorie
import os

class DocumentSecurityTest(TestCase):
    def setUp(self):
        # Création des utilisateurs
        self.admin = User.objects.create_user(username='admin_user', password='password123', role='administrateur')
        self.archiviste_a = User.objects.create_user(username='archiviste_a', password='password123', role='archiviste')
        self.archiviste_b = User.objects.create_user(username='archiviste_b', password='password123', role='archiviste')
        
        # Création d'une catégorie
        self.cat = Categorie.objects.create(nom="Test Category")
        
        # Création d'un document pour Archiviste A
        # Note: On utilise un fichier fictif pour le test
        self.doc_a = Document.objects.create(
            titre="Document A",
            archiviste=self.archiviste_a,
            categorie=self.cat,
            fichier="test_a.pdf"
        )
        
        self.client = Client()

    def test_idor_archivage_restricted(self):
        """Vérifie qu'un archiviste ne peut pas archiver le document d'un autre."""
        self.client.login(username='archiviste_b', password='password123')
        url = reverse('archiver_document', args=[self.doc_a.pk])
        response = self.client.get(url, follow=True)
        # Devrait rediriger avec un message d'erreur et rester actif
        self.doc_a.refresh_from_db()
        self.assertEqual(self.doc_a.statut, 'actif')
        # Vérification du message d'erreur (optionnel mais bon pour l'UX)
        messages = list(response.context['messages'])
        self.assertTrue(any("permission" in m.message.lower() for m in messages))

    def test_admin_can_archive_any(self):
        """Vérifie que l'admin peut archiver n'hui quel document."""
        self.client.login(username='admin_user', password='password123')
        url = reverse('archiver_document', args=[self.doc_a.pk])
        self.client.get(url)
        self.doc_a.refresh_from_db()
        self.assertEqual(self.doc_a.statut, 'archive')

    def test_idor_suppression_restricted(self):
        """Vérifie qu'un archiviste ne peut pas supprimer le document d'un autre."""
        self.client.login(username='archiviste_b', password='password123')
        url = reverse('supprimer_document', args=[self.doc_a.pk])
        # La suppression attend un POST
        response = self.client.post(url, follow=True)
        self.doc_a.refresh_from_db()
        self.assertEqual(self.doc_a.statut, 'actif')

class CategorySecurityTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin_cat', password='password123', role='administrateur')
        self.archiviste = User.objects.create_user(username='archiviste_cat', password='password123', role='archiviste')
        self.cat = Categorie.objects.create(nom="Secret Category")
        self.client = Client()

    def test_archiviste_cannot_delete_category(self):
        """Vérifie qu'un archiviste ne peut pas supprimer une catégorie."""
        self.client.login(username='archiviste_cat', password='password123')
        url = reverse('supprimer_categorie', args=[self.cat.pk])
        response = self.client.post(url)
        # Doit renvoyer une PermissionDenied (403)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Categorie.objects.filter(pk=self.cat.pk).exists())

    def test_admin_can_delete_category(self):
        """Vérifie que l'admin peut supprimer une catégorie."""
        self.client.login(username='admin_cat', password='password123')
        url = reverse('supprimer_categorie', args=[self.cat.pk])
        self.client.post(url)
        self.assertFalse(Categorie.objects.filter(pk=self.cat.pk).exists())

class UserManagementSecurityTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin_user', password='password123', role='administrateur')
        self.archiviste = User.objects.create_user(username='archiviste_user', password='password123', role='archiviste')
        self.client = Client()

    def test_archiviste_cannot_access_user_list(self):
        """Vérifie que l'archiviste ne peut pas voir la liste des utilisateurs."""
        self.client.login(username='archiviste_user', password='password123')
        url = reverse('gestion_utilisateurs')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_archiviste_cannot_create_user(self):
        """Vérifie que l'archiviste ne peut pas créer d'utilisateur."""
        self.client.login(username='archiviste_user', password='password123')
        url = reverse('creer_utilisateur')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
