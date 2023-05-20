from django.urls import path, include
from rest_framework.routers import DefaultRouter
from oktenProject.main.views import UserViewSet, CarBrandViewSet, CarModelsViewSet, AdViewSet, AdCreateView, \
    ConversationCreateView, ManagerCreateView, CarMakeListView, MissingCarMakeRequestCreateView, CurrencyListView, \
    ExchangeRateListView

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'car-brands', CarBrandViewSet)
router.register(r'car-models', CarModelsViewSet)
router.register(r'ads', AdViewSet)

urlpatterns = [
    path('main/', include('main.urls')),
    path('ads/create/', AdCreateView.as_view(), name='ad-create'),
    path('conversations/create/', ConversationCreateView.as_view(), name='conversation-create'),
    path('managers/create/', ManagerCreateView.as_view(), name='manager-create'),
    path('car-makes/', CarMakeListView.as_view(), name='car-makes-list'),
    path('missing-car-make-request/', MissingCarMakeRequestCreateView.as_view(), name='missing-car-make-request'),
    path('currencies/', CurrencyListView.as_view(), name='currency-list'),
    path('exchange-rates/', ExchangeRateListView.as_view(), name='exchange-rate-list'),
]
