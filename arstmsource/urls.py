
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')), # Préfixe toutes les routes de l'application users
    path('api/academic/', include('academic.urls')),
    path('api/institution/', include('institution.urls')),
    path('api/interactions/', include('interactions.urls')),
    path('api/events/', include('events.urls')),
    path('api/shop/', include('shop.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/forum/', include('forum.urls')),
    path('api/analytics/', include('analytics.urls')),
    path('api/library/', include('library.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
