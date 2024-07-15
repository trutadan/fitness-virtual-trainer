from rest_framework import serializers

from .repetition import RepetitionSerializer
from ..models.video import Video


class VideoSerializer(serializers.ModelSerializer):
    repetitions = RepetitionSerializer(many=True, read_only=True)

    class Meta:
        model = Video
        fields = ['id', 'video', 'repetitions', 'exercise_type', 'created_at']
