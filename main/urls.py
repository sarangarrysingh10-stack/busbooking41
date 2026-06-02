from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('inquiry/', views.inquiry, name='inquiry'),
    path('map/', views.map_view, name='map'),

    # Live tracking
    path('tracking/', views.admin_tracking, name='admin_tracking'),
    path('driver/<uuid:token>/', views.driver_app, name='driver_app'),

    # APIs
    path('api/locations/', views.live_locations_api, name='live_locations'),
    path('api/update-location/<uuid:token>/', views.update_location_api, name='update_location'),
]
