from django.urls import include, path

app_name = 'api'
urlpatterns = [
    path('shifts/', include('clock.shifts.api.urls')),
    path('contracts/', include('clock.contracts.api.urls'))
]
