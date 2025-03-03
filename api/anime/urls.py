from django.urls import path, include
from rest_framework.routers import DefaultRouter
from anime import views

router = DefaultRouter()
router.register('watch_status', views.WatchStatusViewSet, basename='watch_status')
router.register('genres', views.GenreViewSet, basename='genres')
router.register('animes', views.AnimeViewSet, basename='animes')
app_name = 'anime'

urlpatterns = [
    path('', include(router.urls))
]