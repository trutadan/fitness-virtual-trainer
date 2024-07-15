from rest_framework import serializers

from .advice import AdviceSerializer
from ..models.repetition import Repetition


class RepetitionSerializer(serializers.ModelSerializer):
    advice = AdviceSerializer(many=True, read_only=True)

    class Meta:
        model = Repetition
        fields = ['repetition', 'advice']
