from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.overview, name='overview'),
    path('bookings/', views.bookings, name='bookings'),
]
