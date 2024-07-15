from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase

from exercise_correction.models.video import Video
from exercise_correction.models.user_profile import UserProfile


class URLStatusTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='12345')
        UserProfile.objects.create(user=self.user)
        self.client.force_authenticate(user=self.user)

    def test_register_url_status(self):
        url = reverse('register')
        data = {
            'username': 'newuser',
            'password': 'newpass123',
            'password2': 'newpass123',
            'email': 'newuser@example.com'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete_account_url_status(self):
        url = reverse('delete_account')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_profile_url_status(self):
        url = reverse('user_profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_exercises_list_url_status(self):
        url = reverse('exercises_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_video_submit_url_status(self):
        url = reverse('video_submit')
        video_file = SimpleUploadedFile("nothing.mp4", b"file_content", content_type="video/mp4")
        data = {'video': video_file, 'type': 'squat'}
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_videos_url_status(self):
        url = reverse('user_videos')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_video_url_status(self):
        video = Video.objects.create(user=self.user, video='nothing.mp4', exercise_type='squat')
        url = reverse('delete_video', args=[video.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
