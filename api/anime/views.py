from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from core.models import WatchStatus, Genre, Anime
from anime import serializers


class BaseAnimeAttrViewSet(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin):
    """
    Base viewset for user-owned anime attributes.
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """
        Return objects for the current authenticated user only.
        """
        assigned_only = bool(int(self.request.query_params.get('assigned_only', 0)))
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(animes__isnull=False)
        return queryset.filter(user=self.request.user).order_by('-name').distinct()

    def perform_create(self, serializer):
        """
        Create a new object (e.g., Genre, WatchStatus).
        """
        serializer.save(user=self.request.user)


class WatchStatusViewSet(viewsets.GenericViewSet, 
                         mixins.ListModelMixin, 
                         mixins.CreateModelMixin, 
                         mixins.UpdateModelMixin, 
                         mixins.DestroyModelMixin):
    """
    Manage watch statuses in the database.
    """
    serializer_class = serializers.WatchStatusSerializer 
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        queryset = WatchStatus.objects.filter(user=self.request.user)

        assigned_only = self.request.query_params.get('assigned_only', None)
        if assigned_only is not None:
            queryset = queryset.filter(animes__isnull=False)  # This filters out unassigned WatchStatus objects.

        queryset = queryset.distinct() 

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class GenreViewSet(BaseAnimeAttrViewSet):
    """
    Manage genres in the database.
    """
    queryset = Genre.objects.all()
    serializer_class = serializers.GenreSerializer

class AnimeViewSet(viewsets.ModelViewSet):
    """
    Manage animes in the database.
    """
    serializer_class = serializers.AnimeSerializer
    queryset = Anime.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def _params_to_ints(self, qs):
        """
        Convert a list of string IDs to a list of integers.
        """
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """
        Retrieve the animes for the authenticated user.
        """
        watch_status = self.request.query_params.get('watch_status')
        genres = self.request.query_params.get('genres')
        queryset = self.queryset

        if watch_status:
            watch_status_ids = self._params_to_ints(watch_status)
            queryset = queryset.filter(watch_status__id__in=watch_status_ids)
        if genres:
            genre_ids = self._params_to_ints(genres)
            queryset = queryset.filter(genres__id__in=genre_ids)

        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """
        Return appropriate serializer class.
        """
        if self.action == 'retrieve':
            return serializers.AnimeDetailSerializer
        elif self.action == 'upload_image':
            return serializers.AnimeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """
        Create a new anime to track.
        """
        genres_data = self.request.data.get("genres", [])
        watch_status = self.request.data.get("watch_status", None)
        anime = serializer.save(user=self.request.user)

        # Ensure WatchStatus is linked correctly
        if watch_status:
            anime.watch_status.user = self.request.user  
            anime.watch_status.save()  

        # Ensure Genres are linked correctly
        if genres_data:
            anime.genres.set(genres_data)  # Assign genres to the anime
