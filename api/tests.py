from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from unittest.mock import patch
from .models import Movie, UserProfile, Rating

class AuthenticatedBaseTest(TestCase):

    def setUp(self):
        # Create a User and UserProfile for authentication
        self.user = User.objects.create_user(
            username='tinmar', 
            email='tinmar@test.com', 
            password='azerty'
        )
        # CRITICAL: Ensure the UserProfile is created!
        self.profile = UserProfile.objects.create(user=self.user)
        
        # Create an APIClient and authenticate the user
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

class WatchListTests(AuthenticatedBaseTest):
    url = '/api/movies/watch_list/'

    def test_get_empty_watchlist(self):
        # Access self.client and self.url, which were inherited
        response = self.client.get(self.url) 
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)