from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from api.models import Movie, Rating, UserProfile
from unittest.mock import patch

TEST_PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']


@override_settings(
    PASSWORD_HASHERS=TEST_PASSWORD_HASHERS,
    DEBUG=False,
)
class RegisterViewTestCase(APITestCase):
    """Tests for the user registration endpoint"""
    
    def setUp(self):
        """Setup that runs before each test"""
        self.register_url = reverse('register')
    
    def test_register_new_user_success(self):
        """Test: Successfully registering a new user"""
        data = {
            'username': 'testuser',
            'password': 'testpass123!',
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
            'password': 'testpass123',
            'email': 'test@example.com'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        # Should fail with 400 BAD REQUEST
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)


@override_settings(
    PASSWORD_HASHERS=TEST_PASSWORD_HASHERS,
    DEBUG=False,
)
class RatingsViewTestCase(APITestCase):
    """Tests for the ratings endpoint"""
    
    def setUp(self):
        """Setup that runs before each test"""
        # Create user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123!',
            email='test@example.com'
        )
        
        # Create UserProfile for the user (FIX)
        self.userprofile = UserProfile.objects.create(user=self.user)
        
        # Get token
        self.token = Token.objects.create(user=self.user)
        # Configure authentication
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        # URLs
        self.ratings_url = reverse('ratings')
        
        # Create a test movie
        self.movie = Movie.objects.create(
            external_id=1234567,  # Use number instead of string
            title='Test Movie',
            poster_url='https://example.com/poster.jpg',
            description='A test movie',
            director='Test Director',
            genre='Action',
            keyword='test',
            year=2024,
            duration=120
        )
    
    def test_create_rating_success(self):
        """Test: Successfully creating a rating"""
        data = {
            'movie': self.movie.external_id,
            'score': 8,
            'comment': 'Great movie!'
        }
        
        response = self.client.post(self.ratings_url, data, format='json')
        
        # Check status code
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check if the rating was created
        self.assertTrue(
            Rating.objects.filter(
                user=self.user,
                movie=self.movie
            ).exists()
        )
        
        # Check returned data
        self.assertEqual(response.data['score'], 8)
        self.assertEqual(response.data['comment'], 'Great movie!')
    
    def test_create_rating_without_authentication(self):
        """Test: Attempting to create a rating without authentication"""
        # Remove credentials
        self.client.credentials()
        
        data = {
            'movie': self.movie.external_id,
            'score': 8,
            'comment': 'Great movie!'
        }
        
        response = self.client.post(self.ratings_url, data, format='json')
        
        # Should fail with 401 UNAUTHORIZED
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_rating_invalid_score(self):
        """Test: Attempting to create a rating with an invalid score (outside range 1–10)"""
        data = {
            'movie': self.movie.external_id,
            'score': 11,  # Invalid
            'comment': 'Great movie!'
        }
        
        response = self.client.post(self.ratings_url, data, format='json')
        
        # Should fail with 400 BAD REQUEST
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_rating_missing_movie(self):
        """Test: Attempting to create a rating without specifying the movie"""
        data = {
            'score': 8,
            'comment': 'Great movie!'
        }
        
        response = self.client.post(self.ratings_url, data, format='json')
        
        # Should fail with 400 BAD REQUEST
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_create_duplicate_rating(self):
        """Test: Attempting to create a duplicate rating for the same movie"""
        # Create first rating
        Rating.objects.create(
            user=self.user,
            movie=self.movie,
            score=8,
            comment='First rating'
        )
        
        # Attempt to create another rating for the same movie
        data = {
            'movie': self.movie.external_id,
            'score': 9,
            'comment': 'Second rating'
        }
        
        response = self.client.post(self.ratings_url, data, format='json')
        
        # Should fail with 400 BAD REQUEST
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_get_all_ratings(self):
        """Test: Get all ratings of the user"""
        # Create some ratings
        Rating.objects.create(
            user=self.user,
            movie=self.movie,
            score=8,
            comment='Great!'
        )
        
        movie2 = Movie.objects.create(
            external_id=7654321,  # Use number
            title='Another Movie',
            poster_url='https://example.com/poster2.jpg',
            description='Another test movie',
            director='Another Director',
            genre='Drama',
            keyword='test2',
            year=2023,
            duration=110
        )
        
        Rating.objects.create(
            user=self.user,
            movie=movie2,
            score=7,
            comment='Good!'
        )
        
        response = self.client.get(self.ratings_url)
        
        # Check status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should return 2 ratings
        self.assertEqual(len(response.data), 2)
    
    def test_update_rating_success(self):
        """Test: Update an existing rating"""
        # Create initial rating
        Rating.objects.create(
            user=self.user,
            movie=self.movie,
            score=8,
            comment='Initial rating'
        )
        
        # Update rating
        data = {
            'movie': self.movie.external_id,
            'score': 9,
            'comment': 'Updated rating'
        }
        
        response = self.client.patch(self.ratings_url, data, format='json')
        
        # Check status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check updated values
        rating = Rating.objects.get(user=self.user, movie=self.movie)
        self.assertEqual(rating.score, 9)
        self.assertEqual(rating.comment, 'Updated rating')
    
    def test_update_nonexistent_rating(self):
        """Test: Attempting to update a rating that does not exist"""
        data = {
            'movie': self.movie.external_id,
            'score': 9,
            'comment': 'Update attempt'
        }
        
        response = self.client.patch(self.ratings_url, data, format='json')
        
        # Should fail with 404 NOT FOUND
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        


@override_settings(
    PASSWORD_HASHERS=TEST_PASSWORD_HASHERS,
    DEBUG=False,
)
class RecommendedMoviesViewTestCase(APITestCase):
    """Tests for the recommended movies endpoint"""
    
    def setUp(self):
        """Setup that runs before each test"""
        # Create user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123!',
            email='test@example.com'
        )
        
        # Create UserProfile
        self.userprofile = UserProfile.objects.create(user=self.user)
        
        # Get token
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        # URLs
        self.recommendations_url = reverse('recommended-movies')
        
        # Create test movies
        self.movie1 = Movie.objects.create(
            external_id=1111111,
            title='Inception',
            poster_url='https://example.com/inception.jpg',
            description='A thief who steals corporate secrets',
            director='Christopher Nolan',
            genre='Sci-Fi',
            keyword='dream',
            year=2010,
            duration=148
        )
        
        self.movie2 = Movie.objects.create(
            external_id=2222222,
            title='Interstellar',
            poster_url='https://example.com/interstellar.jpg',
            description='A team of explorers travel through a wormhole',
            director='Christopher Nolan',
            genre='Sci-Fi',
            keyword='space',
            year=2014,
            duration=169
        )
        
        self.movie3 = Movie.objects.create(
            external_id=3333333,
            title='The Dark Knight',
            poster_url='https://example.com/dark-knight.jpg',
            description='Batman faces the Joker',
            director='Christopher Nolan',
            genre='Action',
            keyword='superhero',
            year=2008,
            duration=152
        )
        
        self.movie4 = Movie.objects.create(
            external_id=4444444,
            title='The Matrix',
            poster_url='https://example.com/matrix.jpg',
            description='A computer hacker learns about reality',
            director='Wachowski Sisters',
            genre='Sci-Fi',
            keyword='simulation',
            year=1999,
            duration=136
        )
    
    def test_get_recommended_movies_success(self):
        """Test 1: Successfully get recommended movies"""
        # Add recommended movies to UserProfile
        self.userprofile.recommended_movies.add(self.movie1, self.movie2)
        
        response = self.client.get(self.recommendations_url)
        
        # Check status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that it returned the recommended movies
        self.assertEqual(len(response.data), 2)
        
        # Check that the correct movies were returned
        movie_ids = [movie['external_id'] for movie in response.data]
        self.assertIn(self.movie1.external_id, movie_ids)
        self.assertIn(self.movie2.external_id, movie_ids)
    
    def test_get_recommended_movies_empty_list(self):
        """Test 2: Get recommendations when there are none"""
        response = self.client.get(self.recommendations_url)
        
        # Check status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that list is empty
        self.assertEqual(len(response.data), 0)
    
    def test_refresh_recommendations_success(self):
        """Test 5: Successfully update/refresh recommendations"""
        # Create some ratings to generate recommendations
        Rating.objects.create(user=self.user, movie=self.movie1, score=9)
        Rating.objects.create(user=self.user, movie=self.movie2, score=8)
        
        response = self.client.patch(self.recommendations_url)
        
        # Check status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that it returned movies (may vary based on recommendation algorithm)
        self.assertIsInstance(response.data, list)
    
    def test_recommended_movies_isolation_between_users(self):
        """Test 9: Verify that recommendations are isolated per user"""
        # Create second user
        user2 = User.objects.create_user(
            username='testuser2',
            password='testpass123!',
            email='test2@example.com'
        )
        userprofile2 = UserProfile.objects.create(user=user2)
        
        # Add different recommendations for each user
        self.userprofile.recommended_movies.add(self.movie1)
        userprofile2.recommended_movies.add(self.movie2, self.movie3)
        
        # Get recommendations for user1 (already authenticated)
        response = self.client.get(self.recommendations_url)
        
        # Check that it only has user1's recommendations
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['external_id'], self.movie1.external_id)
    
    def test_recommended_movies_include_movie_details(self):
        """Test 10: Verify that recommendations include all movie details"""
        self.userprofile.recommended_movies.add(self.movie1)
        
        response = self.client.get(self.recommendations_url)
        
        # Check that it includes the fields that the serializer returns
        movie_data = response.data[0]
        self.assertIn('external_id', movie_data)
        self.assertIn('title', movie_data)
        self.assertIn('genre', movie_data)
        self.assertIn('year', movie_data)
        self.assertIn('poster_url', movie_data)
        self.assertIn('description', movie_data)
        
        # Check correct values
        self.assertEqual(movie_data['title'], 'Inception')
        self.assertEqual(movie_data['external_id'], self.movie1.external_id)
        self.assertEqual(movie_data['genre'], 'Sci-Fi')
        self.assertEqual(movie_data['year'], 2010)
    
    def test_recommended_movies_multiple_genres(self):
        """Test 11: Recommendations can include multiple genres"""
        # Add movies from different genres
        self.userprofile.recommended_movies.add(
            self.movie1,  # Sci-Fi
            self.movie3   # Action
        )
        
        response = self.client.get(self.recommendations_url)
        
        # Check that both were returned
        self.assertEqual(len(response.data), 2)
        
        genres = [movie['genre'] for movie in response.data]
        self.assertIn('Sci-Fi', genres)
        self.assertIn('Action', genres)
    
    def test_add_multiple_recommended_movies(self):
        """Test 12: Add multiple movies to recommendations"""
        # Add multiple movies
        self.userprofile.recommended_movies.add(
            self.movie1,
            self.movie2,
            self.movie3,
            self.movie4
        )
        
        response = self.client.get(self.recommendations_url)
        
        # Check that all were returned
        self.assertEqual(len(response.data), 4)
    
    def test_clear_and_refresh_recommendations(self):
        """Test 13: Clear and regenerate recommendations"""
        # Add initial recommendations
        self.userprofile.recommended_movies.add(self.movie1, self.movie2)
        
        # Check that it has 2
        self.assertEqual(self.userprofile.recommended_movies.count(), 2)
        
        # Simulate refresh that clears and adds new ones
        self.userprofile.recommended_movies.clear()
        self.userprofile.recommended_movies.add(self.movie3, self.movie4)
        
        response = self.client.get(self.recommendations_url)
        
        # Check that it now has the new recommendations
        self.assertEqual(len(response.data), 2)
        movie_ids = [movie['external_id'] for movie in response.data]
        self.assertNotIn(self.movie1.external_id, movie_ids)
        self.assertIn(self.movie3.external_id, movie_ids)
    
    def test_recommendations_based_on_ratings(self):
        """Test 14: Simulate recommendations based on ratings"""
        # Create some ratings
        Rating.objects.create(user=self.user, movie=self.movie1, score=9)
        Rating.objects.create(user=self.user, movie=self.movie2, score=8)
        
        # Simulate that update_recommendations adds similar movies
        self.userprofile.recommended_movies.add(self.movie3)  # Same director
        
        response = self.client.get(self.recommendations_url)
        
        # Check that it received recommendations
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
    
    def test_recommended_movies_not_duplicated(self):
        """Test 15: Don't allow duplicate movies in recommendations"""
        # Try to add the same movie twice
        self.userprofile.recommended_movies.add(self.movie1)
        self.userprofile.recommended_movies.add(self.movie1)
        
        response = self.client.get(self.recommendations_url)
        
        # Check that it only appears once (ManyToMany doesn't allow duplicates)
        self.assertEqual(len(response.data), 1)
