from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoginView, PlatformUserViewSet, LogoutView, register_admin  # Adjust the import as needed

router = DefaultRouter()
router.register('users', PlatformUserViewSet, basename='users') 

urlpatterns = [
    path('', include(router.urls)),  # Include the router's URLs
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('registerAdmin/', register_admin, name='registerAdmin'),
]