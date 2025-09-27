from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import Booking
from .serializers import BookingSerializer
from .permissions import IsAdmin

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        print(f"🔍 Debug: User đang gọi API: {user}, Role: {user.role}")  # Log user
        if user.role == 'admin':
            return Booking.objects.all()
        return Booking.objects.filter(user=user)
    
    def perform_create(self, serializer):
        booking = serializer.save(user=self.request.user)
        self.send_booking_confirmation_email(booking)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if booking.status == 'confirmed' and request.user.role != 'admin':
            return Response(
                {"error": "Không thể hủy lịch đã được xác nhận. Vui lòng liên hệ Admin."},
                status=status.HTTP_400_BAD_REQUEST
            )
        booking.status = 'cancelled'
        booking.save()
        return Response({"message": "Đã hủy lịch hẹn thành công."})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdmin])
    def confirm(self, request, pk=None):
        booking = self.get_object()
        booking.status = 'confirmed'
        booking.save()
        self.send_booking_status_email(booking, "Đã xác nhận")
        return Response({"message": "Đã xác nhận lịch hẹn."})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdmin])
    def complete(self, request, pk=None):
        booking = self.get_object()
        booking.status = 'completed'
        booking.save()
        return Response({"message": "Đã hoàn thành lịch hẹn."})
    
    def send_booking_confirmation_email(self, booking):
        subject = 'Xác nhận đặt lịch làm nail'
        html_message = render_to_string('booking_confirmation_email.html', {
            'user': booking.user,
            'booking': booking,
            'nail_sample': booking.nail_sample,
        })
        plain_message = strip_tags(html_message)
        from_email = settings.EMAIL_HOST_USER
        to_email = booking.user.email
        
        send_mail(
            subject,
            plain_message,
            from_email,
            [to_email],
            html_message=html_message,
            fail_silently=False,
        )
    
    def send_booking_status_email(self, booking, status_text):
        subject = f'Cập nhật trạng thái đặt lịch: {status_text}'
        html_message = render_to_string('booking_status_email.html', {
            'user': booking.user,
            'booking': booking,
            'nail_sample': booking.nail_sample,
            'status': status_text
        })
        plain_message = strip_tags(html_message)
        from_email = settings.EMAIL_HOST_USER
        to_email = booking.user.email
        
        send_mail(
            subject,
            plain_message,
            from_email,
            [to_email],
            html_message=html_message,
            fail_silently=False,
        )