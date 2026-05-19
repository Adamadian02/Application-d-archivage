from django.urls import path
from . import views

urlpatterns = [
    path('documents/', views.liste_documents, name='liste_documents'),
    path('documents/upload/', views.upload_document, name='upload_document'),
    path('documents/<int:pk>/', views.detail_document, name='detail_document'),
    path('documents/<int:pk>/modifier/', views.modifier_document, name='modifier_document'),
    path('documents/<int:pk>/archiver/', views.archiver_document, name='archiver_document'),
    path('documents/<int:pk>/supprimer/', views.supprimer_document, name='supprimer_document'),
    path('documents/<int:pk>/telecharger/', views.telecharger_document, name='telecharger_document'),
    path('recherche/', views.recherche_documents, name='recherche_documents'),
    path('archives/', views.consultation_archives, name='consultation_archives'),
]
