"""autoria_clone URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls')"""

from __main__ import views
from django.urls import path
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from autoria_clone.main.views import UserViewSet, CarBrandViewSet, CarModelViewSet, AdViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'car-brands', CarBrandViewSet)
router.register(r'car-models', CarModelViewSet)
router.register(r'ads', AdViewSet)
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('ads/create/', views.AdCreateView.as_view(), name='ad-create'),
    path('conversations/create/', views.ConversationCreateView.as_view(), name='conversation-create'),
    path('managers/create/', views.ManagerCreateView.as_view(), name='manager-create'),
    path('car-makes/', views.CarMakeListView.as_view(), name='car-makes-list'),
    path('missing-car-make-request/', views.MissingCarMakeRequestCreateView.as_view(), name='missing-car-make-request'),
    path('currencies/', views.CurrencyListView.as_view(), name='currency-list'),
    path('exchange-rates/', views.ExchangeRateListView.as_view(), name='exchange-rate-list'),
]

