from rest_framework import serializers
from core.models import WatchStatus, Genre, Anime

class WatchStatusSerializer(serializers.ModelSerializer):
    """
    Serializer for watch status objects
    """
    class Meta:
        model = WatchStatus
        fields = ('id', 'status', 'progress')
        read_only_fields = ('id',)


class GenreSerializer(serializers.ModelSerializer):
    """
    Serializer for genre objects
    """
    class Meta:
        model = Genre
        fields = ('id', 'name')
        read_only_fields = ('id',)


class AnimeSerializer(serializers.ModelSerializer):
    """
    Serialize an anime
    """
    watch_status = serializers.PrimaryKeyRelatedField(
        queryset = WatchStatus.objects.all()
    )

    genres = serializers.PrimaryKeyRelatedField(
        many = True,
        queryset = Genre.objects.all() 
    )

    class Meta:
        model = Anime
        fields = ('id', 'title', 'description', 'watch_status', 'genres', 'release_date')
        read_only_fields = ('id',)


class AnimeDetailSerializer(AnimeSerializer):
    """Serialize a recipe detail"""
    genres = GenreSerializer(many=True)
    watch_status = WatchStatus()


