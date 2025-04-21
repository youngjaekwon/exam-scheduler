from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()

REGISTER_URL = reverse("users:register")
ME_URL = reverse("users:me")
TOKEN_URL = reverse("users:token_obtain_pair")
TOKEN_REFRESH_URL = reverse("users:token_refresh")


def create_user(username, email, password):
    user = User.objects.create_user(username=username, email=email, password=password)
    return user


class UserRegisterTests(APITestCase):
    def test_user_register__success(self):
        # Given
        payload = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword",
            "password_confirm": "testpassword",
        }

        # When
        response = self.client.post(REGISTER_URL, payload)

        # Then
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, payload["username"])

    def test_user_register__fail_with_password_mismatch(self):
        # Given
        payload = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword",
            "password_confirm": "wrongpassword",
        }

        # When
        response = self.client.post(REGISTER_URL, payload)

        # Then
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)

    def test_user_register__fail_with_existing_username(self):
        # Given
        User.objects.create_user(username="testuser", email="test@example.com", password="testpassword")
        payload = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword",
            "password_confirm": "testpassword",
        }

        # When
        response = self.client.post(REGISTER_URL, payload)

        # Then
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)


class UserMeTests(APITestCase):
    def test_user_me__success(self):
        # Given
        user = create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
        )
        self.client.force_authenticate(user=user)

        # When
        response = self.client.get(ME_URL)

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], user.username)
        self.assertEqual(response.data["email"], user.email)

    def test_user_me__fail_with_unauthorized(self):
        # When
        response = self.client.get(ME_URL)

        # Then
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserTokenTests(APITestCase):
    def test_user_token__success(self):
        # Given
        user = create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
        )
        payload = {
            "username": user.username,
            "password": "testpassword",
        }

        # When
        response = self.client.post(TOKEN_URL, payload)

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_user_token__fail_with_invalid_credentials(self):
        # Given
        user = create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
        )
        payload = {
            "username": user.username,
            "password": "wrongpassword",
        }

        # When
        response = self.client.post(TOKEN_URL, payload)

        # Then
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserTokenRefreshTests(APITestCase):
    def test_user_token_refresh__success(self):
        # Given
        user = create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
        )
        payload = {
            "username": user.username,
            "password": "testpassword",
        }
        response = self.client.post(TOKEN_URL, payload)
        refresh_token = response.data["refresh"]

        # When
        response = self.client.post(TOKEN_REFRESH_URL, {"refresh": refresh_token})

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_user_token_refresh__fail_with_invalid_token(self):
        # Given
        user = create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
        )
        payload = {
            "username": user.username,
            "password": "testpassword",
        }
        response = self.client.post(TOKEN_URL, payload)
        refresh_token = response.data["refresh"]

        # When
        response = self.client.post(TOKEN_REFRESH_URL, {"refresh": "invalidtoken"})

        # Then
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
