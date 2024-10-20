from django.urls import path
from .views import home_view, cv_view

urlpatterns = [
    path('', home_view, name='home'),  # Route pour la page d'accueil
    path('cv/', cv_view, name='cv'),   # Route pour la page de traitement des CV
]
