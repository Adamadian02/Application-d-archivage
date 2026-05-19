# GED Universitaire

Système de Gestion Électronique de Documents pour administration universitaire.

## 🚀 Installation

```bash
# 1. Cloner et installer
pip install -r requirements.txt

# 2. Migrations
python manage.py makemigrations accounts documents categories historique
python manage.py migrate

# 3. Données de démo
python manage.py shell < seed.py

# 4. Lancer
python manage.py runserver
```

## 🔐 Comptes de démonstration

| Rôle | Identifiant | Mot de passe |
|------|-------------|--------------|
| Administrateur | `admin` | `admin123` |
| Archiviste | `archiviste` | `archiviste123` |

## 📁 Structure

```
ged_universitaire/        # Configuration Django
apps/
  accounts/               # Authentification & utilisateurs
  documents/              # Gestion documentaire
  categories/             # Catégories
  historique/             # Logs & historique
templates/
  auth/                   # Connexion, mot de passe oublié
  admin_ged/              # Dashboard, archives, historique système
  archiviste/             # Documents, upload, utilisateurs, catégories
  errors/                 # 403, 404
static/
  css/main.css            # Design system complet
  js/main.js              # Interactions JS

## 🎨 Technologies

- **Backend**: Django 4.2
- **Frontend**: Bootstrap 5 + CSS custom + Chart.js
- **Icons**: Bootstrap Icons
- **Font**: DM Sans (Google Fonts)
```
