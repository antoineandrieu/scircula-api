"""scircula_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from .views import CustomerAnalyticViewSet, CustomerAccessViewSet, CustomerDeleteViewSet, CustomerMeasurementViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'analytics', CustomerAnalyticViewSet,
                basename='customers-analytics')
router.register(r'measurements', CustomerMeasurementViewSet,
                basename='customers-measurement')
router.register(r'delete', CustomerDeleteViewSet,
                basename='customers-delete')
router.register(r'access', CustomerAccessViewSet,
                basename='customers-access')
urlpatterns = router.urls
