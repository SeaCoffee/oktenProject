from rest_framework import serializers
from .models import User, CarBrand, CarModel, Ad

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