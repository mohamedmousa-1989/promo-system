from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError


from rest_framework import serializers

from promoapp.models import Promo


class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ('id', 'username')


class PromoSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Promo
        fields = ('id', 'name', 'points', 'recipient')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['Recipient name'] = instance.recipient.username

        return data


class RemainingPointsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Promo
        fields = ('id', 'name', 'points', 'recipient')

    def to_representation(self, instance):
        return {
            'Promo name': instance.name,
            'Remaining points': instance.points - instance.points_used
            }


class ConsumePromoPointsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Promo
        fields = ('points_used',)

    def to_representation(self, instance):
        return {
            'Points available for you': instance.points - instance.points_used,
            }

