from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import  logout_view, NailSampleViewSet, UserRegistrationView, check_token, UpdateProfilePictureView, UpdateProfileView, user_profile, health_check
from .views_booking import BookingViewSet
router = DefaultRouter()

router.register(r'nails', NailSampleViewSet)
router.register(r'bookings', BookingViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('health/', health_check, name='health_check'),
    path('auth/register/', UserRegistrationView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/check_token/', check_token, name='check_token'),
    path('auth/update_profile/', UpdateProfileView.as_view(), name='update_profile'),
    path('auth/update_profile_picture/', UpdateProfilePictureView.as_view(), name='update_profile_picture'),
    path('auth/user_profile/', user_profile, name='user_profile'),
]