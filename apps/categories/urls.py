from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_categories, name='liste_categories'),
    path('creer/', views.creer_categorie, name='creer_categorie'),
    path('<int:pk>/modifier/', views.modifier_categorie, name='modifier_categorie'),
    path('<int:pk>/supprimer/', views.supprimer_categorie, name='supprimer_categorie'),
]
