from django.urls import include, path
from rest_framework import routers

from clock.shifts.api import views

router = routers.DefaultRouter()
router.register('shifts', views.ShiftViewSet)

urlpatterns = [path('', include(router.urls))]
