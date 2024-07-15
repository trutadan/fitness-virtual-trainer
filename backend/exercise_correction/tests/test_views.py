from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase

from exercise_correction.models.user_profile import UserProfile
from exercise_correction.models.video import Video


class RegisterViewTest(APITestCase):
    def test_register_user(self):
        url = reverse('register')
        data = {
            'username': 'testuser',
            'password': 'testpass123',
            'password2': 'testpass123',
            'email': 'testuser@example.com'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class ExercisesListViewTest(APITestCase):
    def setUp(self):
        self.url = reverse('exercises_list')
        self.user = get_user_model().objects.create_user(username='testuser', password='12345')
        self.client.force_authenticate(user=self.user)

    def test_get_exercises(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)


class DeleteUserViewTest(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='12345')
        self.client.force_authenticate(user=self.user)
        self.url = reverse('delete_account')

    def test_delete_user(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(get_user_model().objects.filter(username='testuser').exists())


class UserProfileViewTest(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='12345')
        self.profile = UserProfile.objects.create(user=self.user, height_cm=170, weight_kg=70.0, gender='M')
        self.client.force_authenticate(user=self.user)
        self.url = reverse('user_profile')

    def test_retrieve_user_profile(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['height_cm'], 170)

    def test_update_user_profile(self):
        data = {'height_cm': 175}
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.height_cm, 175)


class VideoSubmitViewTest(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='12345')
        self.client.force_authenticate(user=self.user)
        self.url = reverse('video_submit')
        self.video_file = SimpleUploadedFile("nothing.mp4", b"file_content", content_type="video/mp4")

    def test_submit_video(self):
        data = {'video': self.video_file, 'type': 'squat'}
        response = self.client.post(self.url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Video.objects.filter(user=self.user).exists())


class UserVideosListViewTest(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='12345')
        self.video = Video.objects.create(user=self.user, video='nothing.mp4', exercise_type='squat')
        self.client.force_authenticate(user=self.user)
        self.url = reverse('user_videos')

    def test_list_user_videos(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.video.id)


class VideoDeleteViewTest(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='12345')
        self.video = Video.objects.create(user=self.user, video='nothing.mp4', exercise_type='squat')
        self.client.force_authenticate(user=self.user)
        self.url = reverse('delete_video', args=[self.video.id])

    def test_delete_video(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Video.objects.filter(id=self.video.id).exists())
