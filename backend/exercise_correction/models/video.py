from django.db import models
from django.conf import settings


class Video(models.Model):
    EXERCISE_CHOICES = [
        ('squat', 'Squat'),
        ('bicep_curl', 'Bicep Curl'),
        ('pushup', 'Pushup'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='videos')
    video = models.FileField(upload_to='submitted_videos/')
    exercise_type = models.CharField(max_length=50, choices=EXERCISE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Video {self.id} uploaded by {self.user.username}"
