from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Anime, Genre, WatchStatus
from anime.serializers import AnimeSerializer, AnimeDetailSerializer

from datetime import date 

ANIMES_URL = reverse('anime:animes-list')

# /api/anime/animes
# api/anime/animes/1

def detail_url(anime_id):
    """Return anime detail URL"""
    return reverse('anime:animes-detail', args=[anime_id])


def sample_genre(user, name='Fantasy'):
    """Create and return a sample genre"""
    return Genre.objects.create(user=user, name=name)


def sample_watchStatus(user, status='watched'):
    """Create and return a sample watch status"""
    return WatchStatus.objects.create(user=user, status=status)


def sample_anime(user, **params):
    """Create and return a sample anime"""
    defaults = {
        'title':"Frieren: Beyond Journey's End",
        'description':'"Sousou no Frieren" (also known as "Frieren: Beyond Journey\'s End") is a Japanese manga and anime series that follows Frieren, a powerful elf mage who traveled with a group of heroes to defeat the Demon King. After their quest is complete, the story focuses on Frieren\'s life as she lives for centuries while her human companions age and pass away. The series explores themes of time, memory, and the emotional impact of outliving those she once considered friends. As Frieren embarks on a new journey with new companions, she reflects on the relationships she had and the changes that come with the passage of time.',
        'release_date': date(2023, 9, 23),
    }
    defaults.update(params)

    return Anime.objects.create(user=user, **defaults)


class PublicAnimeApiTests(TestCase):
    """Test unauthenticated anime API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is requried"""
        res = self.client.get(ANIMES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateAnimeApiTests(TestCase):
    """Test authenticated anime API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@testing.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_animes(self):
        """Test retrieving a list of animes"""
        sample_anime(user=self.user)
        sample_anime(user=self.user)

        res = self.client.get(ANIMES_URL)
        animes = Anime.objects.all().order_by('id')
        serializer = AnimeSerializer(animes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_animes_limited_to_user(self):
        """Test retrieving animes for user"""
        user2 = get_user_model().objects.create_user(
            'other@testmail.com',
            'testpass'
        )
        sample_anime(user=user2)
        sample_anime(user=self.user)
        res = self.client.get(ANIMES_URL)
        animes = Anime.objects.filter(user=self.user)
    
        serializer = AnimeSerializer(animes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_anime_detail(self):
        """Test viewing a anime detail"""
        watch_status = sample_watchStatus(user=self.user)
        anime = sample_anime(user=self.user, watch_status=watch_status)
        anime.genres.add(sample_genre(user=self.user))

        url = detail_url(anime.id)
        res = self.client.get(url)

        serializer = AnimeDetailSerializer(anime)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_anime(self):
        """Test creating anime"""
        watchStatus = sample_watchStatus(user=self.user)
        payload = {
            'title':"Frieren: Beyond Journey's End",
            'description':'"Sousou no Frieren" (also known as "Frieren: Beyond Journey\'s End") is a Japanese manga and anime series that follows Frieren, a powerful elf mage who traveled with a group of heroes to defeat the Demon King. After their quest is complete, the story focuses on Frieren\'s life as she lives for centuries while her human companions age and pass away. The series explores themes of time, memory, and the emotional impact of outliving those she once considered friends. As Frieren embarks on a new journey with new companions, she reflects on the relationships she had and the changes that come with the passage of time.',
            'release_date': date(2023, 9, 23),
            'watch_status': watchStatus.id
        }
        res = self.client.post(ANIMES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        anime = Anime.objects.get(id=res.data['id'])

        # Compare the watch_status correctly
        created_watch_status = anime.watch_status  # Assuming watch_status is a ForeignKey in Anime
        self.assertEqual(created_watch_status.id, watchStatus.id)

        for key in payload.keys():
            # Skip the watch_status field as it's already handled separately
            if key != 'watch_status':
                self.assertEqual(payload[key], getattr(anime, key))


    def test_create_anime_with_genres_and_watch_status(self):
        """Test creating a anime with genres"""
        watchStatus = sample_watchStatus(user=self.user)
        genre1 = sample_genre(self.user, name='Adventure')
        genre2 = sample_genre(self.user, name='Fantasy')
        payload = {
            'title': "Frieren: Beyond Journey's End",
            'description': '"Sousou no Frieren" (also known as "Frieren: Beyond Journey\'s End") is a Japanese manga and anime series that follows Frieren, a powerful elf mage who traveled with a group of heroes to defeat the Demon King. After their quest is complete, the story focuses on Frieren\'s life as she lives for centuries while her human companions age and pass away. The series explores themes of time, memory, and the emotional impact of outliving those she once considered friends. As Frieren embarks on a new journey with new companions, she reflects on the relationships she had and the changes that come with the passage of time.',
            'genres': [genre1.id, genre2.id],
            'release_date': date(2023,9,23),
            'watch_status': watchStatus.id 
        }
        res = self.client.post(ANIMES_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        anime = Anime.objects.get(id=res.data['id'])
        genres = anime.genres.all()

        self.assertEqual(genres.count(), 2)

        self.assertIn(genre1, genres)
        self.assertIn(genre2, genres)

        watchStatus1 = anime.watch_status
        self.assertEqual(watchStatus1, watchStatus)

    

