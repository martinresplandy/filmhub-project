from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class RegisterViewTestCase(APITestCase):
    """Tests for the user registration endpoint"""
    
    def setUp(self):
        """Setup that runs before each test"""
        self.register_url = reverse('register')
    
    def test_register_new_user_success(self):
        """Test: Successfully registering a new user"""
        data = {
            'username': 'testuser',
            'password': 'testpass123!',  # Added special character
            'email': 'test@example.com'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        # Check if status code is 201 CREATED
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check if the token was returned
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)
        
        # Check if the user was created in the database
        self.assertTrue(User.objects.filter(username='testuser').exists())
        
        # Check if the token was created
        user = User.objects.get(username='testuser')
        self.assertTrue(Token.objects.filter(user=user).exists())
    
    def test_register_duplicate_username(self):
        """Test: Trying to register a user with an already existing username"""
        # Create first user
        first_user_data = {
            'username': 'duplicateuser',
            'password': 'testpass123!',
            'email': 'first@example.com'
        }
        self.client.post(self.register_url, first_user_data, format='json')
        
        # Try to create another with the same username
        second_user_data = {
            'username': 'duplicateuser',
            'password': 'anotherpass123!',
            'email': 'another@example.com'
        }
        
        response = self.client.post(self.register_url, second_user_data, format='json')
        
        # Should fail with 400 BAD REQUEST
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Check that the error message mentions the username
        self.assertIn('username', response.data)
    
    def test_register_missing_password(self):
        """Test: Trying to register without a password"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com'
            # Missing password
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        # Should fail with 400 BAD REQUEST
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
    
    def test_register_invalid_password(self):
        """Test: Trying to register with a password without a special character"""
        data = {
            'username': 'testuser',
            'password': 'testpass123',  # No special character
            'email': 'test@example.com'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        # Should fail with 400 BAD REQUEST
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)