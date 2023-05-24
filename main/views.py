from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg
from rest_framework.response import Response
from main.serializers import AdPremiumSerializer
from django_filters.rest_framework import DjangoFilterBackend
from main.models import CustomUser, CarBrand, CarModels, Ad, Conversation, Manager, CarMake, MissingCarMakeRequest, Currency, ExchangeRate, AdPrice
from main.serializers import UserSerializer, CarBrandSerializer, CarModelSerializer, AdSerializer, ConversationSerializer, ManagerSerializer, CarMakeSerializer, MissingCarMakeRequestSerializer, CurrencySerializer, ExchangeRateSerializer
from datetime import date, timedelta
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

class CarBrandViewSet(viewsets.ModelViewSet):
    queryset = CarBrand.objects.all()
    serializer_class = CarBrandSerializer

class CarModelsViewSet(viewsets.ModelViewSet):
    queryset = CarModels.objects.all()
    serializer_class = CarModelSerializer

class AdViewSet(viewsets.ModelViewSet):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['car_model__brand']

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        if request.user.is_premium:
            views = instance.adview_set.all()
            today_views = views.filter(timestamp__date=date.today())
            week_views = views.filter(timestamp__date__gte=date.today() - timedelta(days=7))
            month_views = views.filter(timestamp__date__gte=date.today() - timedelta(days=30))

            statistics = {
                'total_views': views.count(),
                'today_views': today_views.count(),
                'week_views': week_views.count(),
                'month_views': month_views.count(),
                'average_price_region': self.calculate_average_price_region(instance),
                'average_price_ukraine': self.calculate_average_price_ukraine(),
            }

            serializer = AdPremiumSerializer(instance, context={'statistics': statistics})
            return Response(serializer.data)
        else:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)

    def calculate_average_price_region(self, ad):
        region = ad.seller.profile.region
        average_price = Ad.objects.filter(seller__profile__region=region).aggregate(Avg('price'))
        return average_price.get('price__avg')

    def calculate_average_price_ukraine(self):
        average_price = Ad.objects.all().aggregate(Avg('price'))
        return average_price.get('price__avg')

    def calculate_price_in_other_currencies(self, price, base_currency):
        exchange_rates = self.get_exchange_rates()

        base_rate = exchange_rates.get(base_currency)
        price_usd = price / base_rate

        price_other_currencies = {}
        for currency, rate in exchange_rates.items():
            if currency != base_currency:
                price_other = price_usd * rate
                price_other_currencies[currency] = round(price_other, 2)

        return price_other_currencies

    def get_exchange_rates(self):
        exchange_rates = {
            'USD': 0.4
        }

        return exchange_rates

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

        price_other_currencies = self.calculate_price_in_other_currencies(
            serializer.validated_data['price'], serializer.validated_data['currency']
        )

        ad = serializer.save(seller=self.request.user)

        for currency, price in price_other_currencies.items():
            ad_price = AdPrice.objects.create(ad=ad, currency=currency, price=price)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        if instance.edit_attempts >= 3:
            instance.is_active = False
            instance.save()
            return Response({'detail': 'Докликался. Объявление помечено как неактивное.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        instance.edit_attempts += 1
        instance.save()
        return Response(serializer.data)

class AdCreateView(generics.CreateAPIView):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer

    def calculate_price_in_other_currencies(self, price, base_currency):
        exchange_rates = ExchangeRate.objects.all()

        base_rate = exchange_rates.get(currency=base_currency).rate
        price_usd = price / base_rate

        price_other_currencies = {}
        for rate in exchange_rates:
            if rate.currency != base_currency:
                price_other = price_usd * rate.rate
                price_other_currencies[rate.currency.name] = round(price_other, 2)

        return price_other_currencies

class ConversationCreateView(generics.CreateAPIView):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer

class ManagerCreateView(generics.CreateAPIView):
    queryset = Manager.objects.all()
    serializer_class = ManagerSerializer

class CarMakeListView(generics.ListAPIView):
    queryset = CarMake.objects.all()
    serializer_class = CarMakeSerializer

class MissingCarMakeRequestCreateView(generics.CreateAPIView):
    queryset = MissingCarMakeRequest.objects.all()
    serializer_class = MissingCarMakeRequestSerializer

class CurrencyListView(generics.ListAPIView):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer

class ExchangeRateListView(generics.ListAPIView):
    queryset = ExchangeRate.objects.all()
    serializer_class = ExchangeRateSerializer
