from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
    PermissionsMixin
from django.conf import settings

class WatchStatus(models.Model):
    """
    Watch status of an anime for a user
    """
    id = models.BigAutoField(primary_key=True)

    STATUS_CHOICES = [
        ('watching', 'Watching'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('dropped', 'Dropped'),
        ('plan_to_watch', 'Plan to Watch'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='plan_to_watch',
    )

    # Foreign key to user (one user can have multiple watch statuses)
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name="watch_statuses"
    )

    progress = models.IntegerField(default=0)  # How many episodes the user has watched

    def __str__(self):
        # Fetch the first anime associated with this watch status (if any)
        anime_titles = ", ".join(anime.title for anime in self.animes.all()) or "No Anime"
    
        return f"{self.user} - {anime_titles} - {self.status} - {self.progress} episodes"
    

class Genre(models.Model):
    """
    Genre for an anime
    """
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)

    # foreign keys
    # a) link with user model 
    
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name="genres"
    )

    def __str__(self):
        return self.name


class Anime(models.Model):
    """
    main Anime object, belongs to a singular user
    """
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    release_date = models.DateField()
    
    # one user can have multiple animes 
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='animes'
    )

    # One-to-Many: Each anime has a single watch status per user (foreign key to WatchStatus)
    watch_status = models.ForeignKey(
        'WatchStatus',
        on_delete=models.CASCADE,
        related_name="animes",
        null=True
    )

    # Many-to-Many: Anime can have multiple genres
    genres = models.ManyToManyField(
        'Genre',
        related_name="animes"
    ) 

    def __str__(self):
        return self.title