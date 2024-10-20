from django.urls import path
from .views import home_view, cv_view

urlpatterns = [
    path('', home_view, name='home'),
    path('cv/', cv_view, name='cv'),
]
