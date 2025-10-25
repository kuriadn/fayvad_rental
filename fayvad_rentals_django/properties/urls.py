"""
Property management URLs
"""

from django.urls import path
from . import views

app_name = 'properties'

urlpatterns = [
    # Location URLs
    path('locations/', views.location_list, name='location_list'),
    path('locations/create/', views.location_create, name='location_create'),
    path('locations/<uuid:pk>/', views.location_detail, name='location_detail'),
    path('locations/<uuid:pk>/edit/', views.location_update, name='location_update'),
    path('locations/<uuid:pk>/delete/', views.location_delete, name='location_delete'),

    # Room URLs
    path('rooms/', views.room_list, name='room_list'),
    path('rooms/create/', views.room_create, name='room_create'),
    path('rooms/<uuid:pk>/', views.room_detail, name='room_detail'),
    path('rooms/<uuid:pk>/edit/', views.room_update, name='room_update'),
    path('rooms/<uuid:pk>/delete/', views.room_delete, name='room_delete'),
]
