from django.urls import reverse, resolve
from django.test import SimpleTestCase

from exercise_correction.views.authentication import RegisterView
from exercise_correction.views.user import DeleteUserView
from exercise_correction.views.user_profile import UserProfileView
from exercise_correction.views.exercise import ExercisesListView
from exercise_correction.views.video import VideoSubmitView, UserVideosListView, VideoDeleteView


class URLTests(SimpleTestCase):
    def test_register_url_resolves(self):
        url = reverse('register')
        self.assertEqual(resolve(url).func.view_class, RegisterView)

    def test_delete_account_url_resolves(self):
        url = reverse('delete_account')
        self.assertEqual(resolve(url).func.view_class, DeleteUserView)

    def test_user_profile_url_resolves(self):
        url = reverse('user_profile')
        self.assertEqual(resolve(url).func.view_class, UserProfileView)

    def test_exercises_list_url_resolves(self):
        url = reverse('exercises_list')
        self.assertEqual(resolve(url).func.view_class, ExercisesListView)

    def test_video_submit_url_resolves(self):
        url = reverse('video_submit')
        self.assertEqual(resolve(url).func.view_class, VideoSubmitView)

    def test_user_videos_url_resolves(self):
        url = reverse('user_videos')
        self.assertEqual(resolve(url).func.view_class, UserVideosListView)

    def test_delete_video_url_resolves(self):
        url = reverse('delete_video', args=[1])
        self.assertEqual(resolve(url).func.view_class, VideoDeleteView)
