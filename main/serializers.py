from rest_framework import serializers
from main.models import CustomUser, CarBrand, CarModels, Ad, Role, \
    Conversation, Manager, CarMake, MissingCarMakeRequest, Currency, ExchangeRate, AdPrice
from datetime import date, timedelta
from django.db.models import Avg
from rest_framework_simplejwt.tokens import RefreshToken


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'is_premium', 'account_type', 'roles')


class CarBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarBrand
        fields = ('id', 'name')


class CarModelSerializer(serializers.ModelSerializer):
    brand = CarBrandSerializer()

    class Meta:
        model = CarModels
        fields = ('id', 'name', 'brand')


class AdPriceSerializer(serializers.ModelSerializer):
    currency = serializers.StringRelatedField()

    class Meta:
        model = AdPrice
        fields = ('id', 'currency', 'price')


class AdSerializer(serializers.ModelSerializer):
    car_model = CarModelSerializer()
    seller = UserSerializer()
    prices = AdPriceSerializer(many=True)

    class Meta:
        model = Ad
        fields = ('id', 'title', 'description', 'price', 'currency', 'car_model', 'seller', 'prices')

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


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ('id', 'buyer', 'seller', 'ad', 'created_at')


class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manager
        fields = '__all__'


class CarMakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarMake
        fields = ('id', 'name')


class MissingCarMakeRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = MissingCarMakeRequest
        fields = ('id', 'car_make', 'seller', 'created_at')


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ('id', 'name')


class ExchangeRateSerializer(serializers.ModelSerializer):
    currency = CurrencySerializer()

    class Meta:
        model = ExchangeRate
        fields = ('id', 'currency', 'rate', 'date')


class TokenObtainSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password', '')

        if email and password:
            user = CustomUser.objects.filter(email=email).first()

            if user and user.check_password(password):
                refresh = RefreshToken.for_user(user)
                attrs['refresh'] = str(refresh)
                attrs['access'] = str(refresh.access_token)
                attrs['user'] = user
                return attrs
            raise serializers.ValidationError('Invalid email or password')
        raise serializers.ValidationError('Email and password are required')

