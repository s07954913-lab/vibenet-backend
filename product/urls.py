from django.urls import path
from . import views

urlpatterns = [
    path('save-search/', views.save_search, name='save-search'),
]