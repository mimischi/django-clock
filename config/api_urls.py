from django.urls import include, path

urlpatterns = [
    path('shifts/', include('clock.shifts.api.urls')),
    path('contracts/', include('clock.contracts.api.urls'))
]
