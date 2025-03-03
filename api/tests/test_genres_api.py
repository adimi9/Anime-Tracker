from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Genre, Anime, WatchStatus
from anime.serializers import GenreSerializer

from datetime import date 

GENRE_URL = reverse('anime:genres-list')

class PublicGenreApiTests(TestCase):
    """
    Test the publicly available genre API
    """
    def setUp(self):
        self.client = APIClient()
        

    def test_login_required(self):
        """
        Test that login is required to access the endpoint
        """
        # Make request without authentication
        res = self.client.get(GENRE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateGenreApiTests(TestCase):
    """
    Test the private genre API
    """
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test2@testmail.com',
            password='testpass',
            username='testuser'
        )
        self.client.force_authenticate(self.user)


    def test_retrieve_genre(self):
        """
        Test retrieving genre of an anime
        """
        # Creating a single genre linked to the user
        Genre.objects.create(user=self.user, name='watching')
        Genre.objects.create(user=self.user, name='completed')

        res = self.client.get(GENRE_URL)
        genres = Genre.objects.all().order_by('-name')
        serializer = GenreSerializer(genres, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_genre_limited_to_user(self):
        """
        "Test that the genre for the authenticated user is returned
        """
        user2 = get_user_model().objects.create_user(
            email='test2@testmail.com',
            password='testpass2',
            username='testuser2'
        )

        Genre.objects.create(user=user2, name='completed')
        genre = Genre.objects.create(user=self.user, name='on_hold')

        res = self.client.get(GENRE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], genre.name)

    def test_create_genre_successful(self):
        """
        Test create a new genre
        """
        payload = {
            'name': 'Adventure',
        }
        self.client.post(GENRE_URL, payload)

        exists = Genre.objects.filter(
            user=self.user,
            name=payload['name'],
        ).exists()
        self.assertTrue(exists)

    def test_create_genre_invalid(self):
        """
        Test creating invalid genre fails
        """
        payload = {
            'name': '',
        }
        res = self.client.post(GENRE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_genre_assigned_to_animes(self):
        """
        Test filtering genres by those assigned to animes
        """
        # Create the first Anime and Genre assigned to it
        genre1 = Genre.objects.create(
            user=self.user, name='Drama'
        )

        # Create the second Genre and assign it to anime2
        genre2 = Genre.objects.create(
            user=self.user, name='Adventure'
        )

        watchStatus = WatchStatus.objects.create(user=self.user, status="plan_to_watch")

        anime = Anime.objects.create(
            title="Frieren: Beyond Journey's End",
            description='"Sousou no Frieren" (also known as "Frieren: Beyond Journey\'s End") is a Japanese manga and anime series that follows Frieren, a powerful elf mage who traveled with a group of heroes to defeat the Demon King. After their quest is complete, the story focuses on Frieren\'s life as she lives for centuries while her human companions age and pass away. The series explores themes of time, memory, and the emotional impact of outliving those she once considered friends. As Frieren embarks on a new journey with new companions, she reflects on the relationships she had and the changes that come with the passage of time.',
            release_date=date(2023, 9, 23),
            user=self.user,
            watch_status = watchStatus
        )

        anime.genres.set([genre1.id])

        res = self.client.get(GENRE_URL, {'assigned_only': 1})

        # Serialize both Genre objects
        serializer1 = GenreSerializer(genre1)
        serializer2 = GenreSerializer(genre2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_genre_assigned_unique(self):
        """Test filtering genre by assigned returns unique items"""
        genre = Genre.objects.create(user=self.user, name='Adventure')
        Genre.objects.create(user=self.user, name='plan_to_watch')

        watchStatus = WatchStatus.objects.create(user=self.user, status="plan_to_watch")

        anime1 = Anime.objects.create(
            title="Frieren: Beyond Journey's End",
            description='"Sousou no Frieren" (also known as "Frieren: Beyond Journey\'s End") is a Japanese manga and anime series that follows Frieren, a powerful elf mage who traveled with a group of heroes to defeat the Demon King. After their quest is complete, the story focuses on Frieren\'s life as she lives for centuries while her human companions age and pass away. The series explores themes of time, memory, and the emotional impact of outliving those she once considered friends. As Frieren embarks on a new journey with new companions, she reflects on the relationships she had and the changes that come with the passage of time.',
            release_date=date(2023, 9, 23),
            user=self.user,
            watch_status=watchStatus
        )

        anime1.genres.set([genre.id])

        anime2 = Anime.objects.create(
            title= 'One Piece',
            description= 'One Piece is a legendary anime and manga series created by Eiichiro Oda. It follows the adventures of Monkey D. Luffy, a young pirate with the ability to stretch his body like rubber after eating a Devil Fruit. Luffy sets sail with his crew, the Straw Hat Pirates, in search of the ultimate treasure, the One Piece, to become the Pirate King.',
            release_date= date(2005, 9, 7),
            user=self.user,
            watch_status=watchStatus
        )

        anime2.genres.set([genre.id])
        res = self.client.get(GENRE_URL, {'assigned_only': 1})
        self.assertEqual(len(res.data), 1)