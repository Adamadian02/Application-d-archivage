from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('apps.accounts.urls')),
    path('dashboard/', include('apps.documents.urls')),
    path('categories/', include('apps.categories.urls')),
    path('historique/', include('apps.historique.urls')),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='partials/profil.html', success_url='/profil/'), name='password_change'),
    path('', include('apps.accounts.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler403 = 'apps.accounts.views.error_403'
handler404 = 'apps.accounts.views.error_404'
