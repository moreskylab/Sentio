from django.urls import path
from .views import recommend_articles

urlpatterns = [
    path('api/recommend/', recommend_articles, name='recommend'),
]