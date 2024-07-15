from rest_framework import serializers

from ..models.advice import Advice


class AdviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advice
        fields = ['category', 'text', 'correction_level']
