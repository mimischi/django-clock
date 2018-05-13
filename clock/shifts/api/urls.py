# from django.urls import include, path
# from rest_framework import routers
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from clock.shifts.api import views

# router = routers.DefaultRouter()
# router.register('shifts', views.ShiftOverlapView, base_name='test')

urlpatterns = [
    path('', views.api_root),
    path(
        'overlap/<str:started>/<str:finished>/<int:contract>/<str:reoccuring>/<int:pk>/',
        views.ShiftOverlapView.as_view(),
        name='overlap-list'
    )
]

urlpatterns = format_suffix_patterns(urlpatterns)
