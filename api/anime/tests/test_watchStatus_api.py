from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import WatchStatus, Anime
from anime.serializers import WatchStatusSerializer

from datetime import date 

WATCHSTATUS_URL = reverse('anime:watch_status-list')

class PublicWatchStatusApiTests(TestCase):
    """
    Test the publicly available watch status API
    """
    def setUp(self):
        self.client = APIClient()
        

    def test_login_required(self):
        """
        Test that login is required to access the endpoint
        """
        # Make request without authentication
        res = self.client.get(WATCHSTATUS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateWatchStatusApiTests(TestCase):
    """
    Test the private watch status API
    """
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test2@testmail.com',
            password='testpass',
            username='testuser'
        )
        self.client.force_authenticate(self.user)


    def test_retrieve_watchStatus(self):
        """
        Test retrieving watch status of an anime
        """
        # Creating a single watch status linked to the user
        WatchStatus.objects.create(user=self.user, status='watching')
        WatchStatus.objects.create(user=self.user, status='completed')

        res = self.client.get(WATCHSTATUS_URL)
        watch_statuses = WatchStatus.objects.all().order_by('-status')
        serializer = WatchStatusSerializer(watch_statuses, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_watchStatus_limited_to_user(self):
        """
        "Test that the watch status for the authenticated user is returned
        """
        user2 = get_user_model().objects.create_user(
            email='test2@testmail.com',
            password='testpass2',
            username='testuser2'
        )

        WatchStatus.objects.create(user=user2, status='completed')
        watchStatus = WatchStatus.objects.create(user=self.user, status='on_hold')

        res = self.client.get(WATCHSTATUS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['status'], watchStatus.status)

    def test_create_watchStatus_successful(self):
        """
        Test create a new watch status
        """
        payload = {
            'status': 'dropped',
        }
        self.client.post(WATCHSTATUS_URL, payload)

        exists = WatchStatus.objects.filter(
            user=self.user,
            status=payload['status'],
        ).exists()
        self.assertTrue(exists)

    def test_create_watchStatus_invalid(self):
        """
        Test creating invalid watch status fails
        """
        payload = {
            'status': 'not_interested',
        }
        res = self.client.post(WATCHSTATUS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_watchStatus_assigned_to_animes(self):
        """
        Test filtering watch statuses by those assigned to animes
        """
        # Create the first Anime and WatchStatus assigned to it
        watchStatus1 = WatchStatus.objects.create(
            user=self.user, status='watching'
        )

        # Create the second WatchStatus and assign it to anime2
        watchStatus2 = WatchStatus.objects.create(
            user=self.user, status='completed'
        )

        Anime.objects.create(
            title="Frieren: Beyond Journey's End",
            description='"Sousou no Frieren" (also known as "Frieren: Beyond Journey\'s End") is a Japanese manga and anime series that follows Frieren, a powerful elf mage who traveled with a group of heroes to defeat the Demon King. After their quest is complete, the story focuses on Frieren\'s life as she lives for centuries while her human companions age and pass away. The series explores themes of time, memory, and the emotional impact of outliving those she once considered friends. As Frieren embarks on a new journey with new companions, she reflects on the relationships she had and the changes that come with the passage of time.',
            release_date=date(2023, 9, 23),
            user=self.user,
            watch_status = watchStatus1
        )

        res = self.client.get(WATCHSTATUS_URL, {'assigned_only': 1})

        # Serialize both WatchStatus objects
        serializer1 = WatchStatusSerializer(watchStatus1)
        serializer2 = WatchStatusSerializer(watchStatus2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_watchStatus_assigned_unique(self):
        """Test filtering watchStatus by assigned returns unique items"""
        watchStatus = WatchStatus.objects.create(user=self.user, status='completed')
        WatchStatus.objects.create(user=self.user, status='plan_to_watch')

        anime1 = Anime.objects.create(
            title="Frieren: Beyond Journey's End",
            description='"Sousou no Frieren" (also known as "Frieren: Beyond Journey\'s End") is a Japanese manga and anime series that follows Frieren, a powerful elf mage who traveled with a group of heroes to defeat the Demon King. After their quest is complete, the story focuses on Frieren\'s life as she lives for centuries while her human companions age and pass away. The series explores themes of time, memory, and the emotional impact of outliving those she once considered friends. As Frieren embarks on a new journey with new companions, she reflects on the relationships she had and the changes that come with the passage of time.',
            release_date=date(2023, 9, 23),
            user=self.user,
            watch_status = watchStatus
        )

        anime2 = Anime.objects.create(
            title= 'One Piece',
            description= 'One Piece is a legendary anime and manga series created by Eiichiro Oda. It follows the adventures of Monkey D. Luffy, a young pirate with the ability to stretch his body like rubber after eating a Devil Fruit. Luffy sets sail with his crew, the Straw Hat Pirates, in search of the ultimate treasure, the One Piece, to become the Pirate King.',
            release_date= date(2005, 9, 7),
            user=self.user,
            watch_status = watchStatus
        )

        res = self.client.get(WATCHSTATUS_URL, {'assigned_only': 1})
        self.assertEqual(len(res.data), 1)