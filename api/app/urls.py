from django.urls import path, include 
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('api/user/', include('user.urls')),
    path('api/anime/', include('anime.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)