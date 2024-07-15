from rest_framework import serializers

from ..models.user_profile import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ('birthday', 'height_cm', 'weight_kg', 'gender', 'avatar', 'username')

    def get_username(self, obj):
        return obj.user.username

    def to_internal_value(self, data):
        _data = data.copy()
        gender_full_to_short = {'Male': 'M', 'Female': 'F', 'Other': 'O'}
        if 'gender' in _data and _data['gender'] in gender_full_to_short:
            _data['gender'] = gender_full_to_short[_data['gender']]
        return super().to_internal_value(_data)

    def to_representation(self, instance):
        gender_short_to_full = {'M': 'Male', 'F': 'Female', 'O': 'Other'}
        ret = super().to_representation(instance)
        if 'gender' in ret:
            ret['gender'] = gender_short_to_full.get(ret['gender'], ret['gender'])
        return ret
