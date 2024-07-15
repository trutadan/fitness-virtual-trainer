from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models.advice import Advice
from ..models.repetition import Repetition
from ..models.user_profile import UserProfile
from ..models.video import Video

import os


class VideoModelTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='12345')
        self.video_file = SimpleUploadedFile("test_video.mp4", b"file_content", content_type="video/mp4")
        self.video = Video.objects.create(user=self.user, video=self.video_file, exercise_type='squat')

    def test_video_creation(self):
        self.assertEqual(str(self.video), f"Video {self.video.id} uploaded by {self.user.username}")

    def test_video_deletion(self):
        video_path = self.video.video.path
        self.video.delete()
        self.assertFalse(os.path.isfile(video_path))


class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='12345')
        self.profile = UserProfile.objects.create(user=self.user, height_cm=170, weight_kg=70.0, gender='M')

    def test_userprofile_creation(self):
        self.assertEqual(str(self.profile), f"{self.user.username}'s profile")


class RepetitionModelTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='12345')
        self.video_file = SimpleUploadedFile("test_video.mp4", b"file_content", content_type="video/mp4")
        self.video = Video.objects.create(user=self.user, video=self.video_file, exercise_type='squat')
        self.repetition_file = SimpleUploadedFile("test_repetition.mp4", b"file_content", content_type="video/mp4")
        self.repetition = Repetition.objects.create(video=self.video, repetition=self.repetition_file)

    def test_repetition_creation(self):
        self.assertEqual(str(self.repetition), f"Repetition {self.repetition.id} of Video {self.video.id}")

    def test_repetition_deletion(self):
        repetition_path = self.repetition.repetition.path
        self.repetition.delete()
        self.assertFalse(os.path.isfile(repetition_path))

    def test_video_deletion_also_deletes_repetitions(self):
        repetition_path = self.repetition.repetition.path
        self.video.delete()
        self.assertFalse(os.path.isfile(repetition_path))


class AdviceModelTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='12345')
        self.video_file = SimpleUploadedFile("test_video.mp4", b"file_content", content_type="video/mp4")
        self.video = Video.objects.create(user=self.user, video=self.video_file, exercise_type='squat')
        self.repetition_file = SimpleUploadedFile("test_repetition.mp4", b"file_content", content_type="video/mp4")
        self.repetition = Repetition.objects.create(video=self.video, repetition=self.repetition_file)
        self.advice = Advice.objects.create(repetition=self.repetition, category='posture', text='Keep your back straight.', correction_level=2)

    def test_advice_creation(self):
        self.assertEqual(str(self.advice), f"Advice of type {self.advice.category} for repetition {self.repetition.id} with level {self.advice.correction_level}")
        self.assertEqual(self.advice.category, 'posture')
        self.assertEqual(self.advice.text, 'Keep your back straight.')
        self.assertEqual(self.advice.correction_level, 2)


if __name__ == '__main__':
    TestCase.main()
