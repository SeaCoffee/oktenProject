from django.shortcuts import render
from rest_framework import viewsets
from .models import User, CarBrand, CarModel, Ad, ForbiddenWord
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer, CarBrandSerializer, CarModelSerializer, AdSerializer
from datetime import date, timedelta
from django.db.models import Avg, Count
from django.utils import timezone
from rest_framework.response import Response
from autoria_clone.main.serializers import AdPremiumSerializer
from django_filters.rest_framework import DjangoFilterBackend


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class CarBrandViewSet(viewsets.ModelViewSet):
    queryset = CarBrand.objects.all()
    serializer_class = CarBrandSerializer

class CarModelViewSet(viewsets.ModelViewSet):
    queryset = CarModel.objects.all()
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

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)


        if instance.edit_attempts >= 3:
            instance.is_active = False
            instance.save()
            return Response(
                {'detail': 'Превышено количество попыток редактирования. Объявление помечено как неактивное.'})

        serializer.save()
        instance.edit_attempts += 1
        instance.save()
        return Response(serializer.data)