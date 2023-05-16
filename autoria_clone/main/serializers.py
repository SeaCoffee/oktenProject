from rest_framework import serializers
from .models import User, CarBrand, CarModel, Ad
from datetime import date, timedelta
from django.db.models import Avg

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'is_premium')

class CarBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarBrand
        fields = ('id', 'name')

class CarModelSerializer(serializers.ModelSerializer):
    brand = CarBrandSerializer()
    class Meta:
        model = CarModel
        fields = ('id', 'name', 'brand')

class AdSerializer(serializers.ModelSerializer):
    car_model = CarModelSerializer()
    seller = UserSerializer()
    class Meta:
        model = Ad
        fields = ('id', 'title', 'description', 'price', 'currency', 'car_model', 'seller')

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        user = self.context['request'].user
        if user.is_authenticated and user.is_premium:
            today = date.today()
            week_ago = today - timedelta(days=7)
            month_ago = today - timedelta(days=30)

            statistics = {
                'views_total': instance.views_total,
                'views_today': instance.views.filter(timestamp__date=today).count(),
                'views_week': instance.views.filter(timestamp__date__range=[week_ago, today]).count(),
                'views_month': instance.views.filter(timestamp__date__range=[month_ago, today]).count(),
                'average_price_region': Ad.objects.filter(car_model__brand=instance.car_model.brand).aggregate(
                    Avg('price')),
                'average_price_ukraine': Ad.objects.all().aggregate(Avg('price'))
            }

            representation['statistics'] = statistics

        return representation

class AdPremiumSerializer(serializers.ModelSerializer):
    statistics = serializers.SerializerMethodField()

    class Meta:
        model = Ad
        fields = ('id', 'title', 'description', 'price', 'currency', 'car_model', 'seller', 'statistics')

    def get_statistics(self, obj):
        return self.context['statistics']