from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from recommendations.views import ArticleViewSet, recommend_articles, dashboard
from django.views.generic.base import RedirectView

# Create a router for the ViewSet
router = DefaultRouter()
router.register(r'articles', ArticleViewSet)

urlpatterns = [
    path('accounts/', include('allauth.urls')), # Includes login, logout, signup, google
    path('', RedirectView.as_view(pattern_name='dashboard', permanent=False)),
    path('admin/', admin.site.urls),
    
    # The Router generates all CRUD URLs automatically
    path('api/', include(router.urls)), 
    
    # Custom Endpoint for Search/Recommendations
    path('api/recommend/', recommend_articles, name='recommend'),

    path('dashboard/', dashboard, name='dashboard'),
]