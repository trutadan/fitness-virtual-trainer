from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from exercise_correction.models.advice import Advice
from exercise_correction.models.repetition import Repetition
from exercise_correction.models.user_profile import UserProfile
from exercise_correction.models.video import Video

from ..serializers.advice import AdviceSerializer
from ..serializers.authentication import RegisterSerializer
from ..serializers.repetition import RepetitionSerializer
from ..serializers.user_profile import UserProfileSerializer
from ..serializers.video import VideoSerializer


class AdviceSerializerTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='12345')
        self.video = Video.objects.create(user=self.user, video=SimpleUploadedFile("test_video.mp4", b"file_content"), exercise_type='squat')
        self.repetition = Repetition.objects.create(video=self.video, repetition=SimpleUploadedFile("test_repetition.mp4", b"file_content"))
        self.advice = Advice.objects.create(repetition=self.repetition, category='posture', text='Keep your back straight.', correction_level=2)

    def test_advice_serializer(self):
        serializer = AdviceSerializer(self.advice)
        data = serializer.data
        self.assertEqual(set(data.keys()), set(['category', 'text', 'correction_level']))
        self.assertEqual(data['category'], self.advice.category)
        self.assertEqual(data['text'], self.advice.text)
        self.assertEqual(data['correction_level'], self.advice.correction_level)


class RegisterSerializerTest(TestCase):
    def test_register_serializer(self):
        data = {
            'username': 'newuser',
            'password': 'newpassword',
            'password2': 'newpassword',
            'email': 'newuser@example.com'
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, data['username'])
        self.assertEqual(user.email, data['email'])
        self.assertTrue(user.check_password(data['password']))

    def test_register_serializer_password_mismatch(self):
        data = {
            'username': 'newuser',
            'password': 'newpassword',
            'password2': 'wrongpassword',
            'email': 'newuser@example.com'
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)


class RepetitionSerializerTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='12345')
        self.video = Video.objects.create(user=self.user, video=SimpleUploadedFile("test_video.mp4", b"file_content"), exercise_type='squat')
        self.repetition = Repetition.objects.create(video=self.video, repetition=SimpleUploadedFile("test_repetition.mp4", b"file_content"))
        self.advice = Advice.objects.create(repetition=self.repetition, category='posture', text='Keep your back straight.', correction_level=2)

    def test_repetition_serializer(self):
        serializer = RepetitionSerializer(self.repetition)
        data = serializer.data
        self.assertEqual(set(data.keys()), set(['repetition', 'advice']))
        self.assertEqual(len(data['advice']), 1)
        self.assertEqual(data['advice'][0]['category'], self.advice.category)
        self.assertEqual(data['advice'][0]['text'], self.advice.text)
        self.assertEqual(data['advice'][0]['correction_level'], self.advice.correction_level)


class UserProfileSerializerTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='12345')
        self.profile = UserProfile.objects.create(user=self.user, height_cm=170, weight_kg=70.0, gender='M')

    def test_userprofile_serializer(self):
        serializer = UserProfileSerializer(self.profile)
        data = serializer.data
        self.assertEqual(set(data.keys()), set(['birthday', 'height_cm', 'weight_kg', 'gender', 'avatar', 'username']))
        self.assertEqual(data['username'], self.user.username)
        self.assertEqual(data['height_cm'], self.profile.height_cm)
        self.assertEqual(float(data['weight_kg']), self.profile.weight_kg)
        self.assertEqual(data['gender'], 'Male')

    def test_userprofile_serializer_gender_conversion(self):
        data = {
            'height_cm': 180,
            'weight_kg': 75.0,
            'gender': 'Female'
        }
        serializer = UserProfileSerializer(instance=self.profile, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_profile = serializer.save()
        self.assertEqual(updated_profile.gender, 'F')


class VideoSerializerTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='12345')
        self.video = Video.objects.create(user=self.user, video=SimpleUploadedFile("test_video.mp4", b"file_content"), exercise_type='squat')
        self.repetition = Repetition.objects.create(video=self.video, repetition=SimpleUploadedFile("test_repetition.mp4", b"file_content"))
        self.advice = Advice.objects.create(repetition=self.repetition, category='posture', text='Keep your back straight.', correction_level=2)

    def test_video_serializer(self):
        serializer = VideoSerializer(self.video)
        data = serializer.data
        self.assertEqual(set(data.keys()), set(['id', 'video', 'repetitions', 'exercise_type', 'created_at']))
        self.assertEqual(len(data['repetitions']), 1)
        self.assertEqual(data['repetitions'][0]['repetition'], self.repetition.repetition.url)
        self.assertEqual(len(data['repetitions'][0]['advice']), 1)
        self.assertEqual(data['repetitions'][0]['advice'][0]['category'], self.advice.category)
        self.assertEqual(data['repetitions'][0]['advice'][0]['text'], self.advice.text)
        self.assertEqual(data['repetitions'][0]['advice'][0]['correction_level'], self.advice.correction_level)


if __name__ == '__main__':
    TestCase.main()