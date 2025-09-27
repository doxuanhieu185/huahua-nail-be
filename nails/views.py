from django.shortcuts import render

# Create your views here.
from rest_framework import status, viewsets, permissions, generics, pagination
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import logout
from .models import CustomUser, NailSample
from .serializers import UserSerializer, UserRegistrationSerializer, NailSampleSerializer, UpdateProfileSerializer, UpdateProfilePictureSerializer
from .permissions import IsAdmin
from rest_framework.parsers import MultiPartParser, FormParser
import os
from django.conf import settings
from django.db import connection
from django.http import JsonResponse


import logging

logger = logging.getLogger(__name__)

def health_check(request):
    """
    Health check endpoint for Kubernetes liveness/readiness probes
    """
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        
        return JsonResponse({
            'status': 'healthy',
            'database': 'connected',
            'version': getattr(settings, 'APP_VERSION', '1.0.0')
        }, status=200)
    
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e)
        }, status=503)

class UserRegistrationView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        # Kiểm tra dữ liệu đầu vào mà không raise exception
        if not serializer.is_valid(raise_exception=False):
            return Response({
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Kiểm tra các validation tùy chỉnh
        validated_data = serializer.validated_data
        if not validated_data.get('valid', True):
            return Response({
                'status': 'error',
                'errors': validated_data.get('errors', {})
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Tạo user
        try:
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'status': 'success',
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UpdateProfileView(generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UpdateProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class UpdateProfilePictureView(generics.UpdateAPIView):
    serializer_class = UpdateProfilePictureSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get_object(self):
        return self.request.user  # Lấy user hiện tại

    def perform_update(self, serializer):
        user = self.get_object()

        if user.profile_picture:
            old_image_path = os.path.join(settings.MEDIA_ROOT, str(user.profile_picture))
            if os.path.exists(old_image_path):
                os.remove(old_image_path)
                print(f"Đã xóa ảnh cũ: {old_image_path}")
        serializer.save()

    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(instance=self.get_object(), data=request.data, partial=True)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({
                "message": "Ảnh đại diện đã cập nhật!",
                "profile_picture": serializer.instance.profile_picture.url
            })
        return Response(serializer.errors, status=400)
    
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_profile(request):
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    print("Received data:", request.data)  # Debug log

    refresh_token = request.data.get("refresh")
    if not refresh_token:
        return Response({"detail": "Thiếu refresh token"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"detail": "Đăng xuất thành công"}, status=status.HTTP_200_OK)
    except Exception as e:
        print("Logout error:", str(e))  # Debug log
        return Response({"detail": "Lỗi khi đăng xuất"}, status=status.HTTP_400_BAD_REQUEST)


class NailSampleViewSet(viewsets.ModelViewSet):
    queryset = NailSample.objects.all()
    serializer_class = NailSampleSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsAdminUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]
    
class NailSamplePagination(pagination.PageNumberPagination):
    page_size = 10  
    page_size_query_param = 'page_size'
    max_page_size = 100
    
class NailSampleViewSet(viewsets.ReadOnlyModelViewSet):  
    queryset = NailSample.objects.all().order_by('-created_at')  
    serializer_class = NailSampleSerializer
    permission_classes = [AllowAny]
    pagination_class = NailSamplePagination

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def check_token(request):
    return Response({"message": "Token is valid"}, status=200)