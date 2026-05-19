from django.urls import path
from . import views

urlpatterns = [
    path('systeme/', views.historique_systeme, name='historique_systeme'),
    path('personnel/', views.historique_personnel, name='historique_personnel'),
]
