from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', _('Admin')
        USER = 'user', _('User')
    
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.USER,
    )
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    username = models.CharField(max_length=150, unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser
    
    def __str__(self):
        return self.email

class NailSample(models.Model):
    title = models.CharField(max_length=255, default="")
    image = models.ImageField(upload_to='nails/')
    detail = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Nail Sample {self.id}"

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Đang chờ'),
        ('confirmed', 'Đã xác nhận'),
        ('cancelled', 'Đã hủy'),
        ('completed', 'Đã hoàn thành'),
    )
    
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='bookings')
    nail_sample = models.ForeignKey('NailSample', on_delete=models.SET_NULL, null=True, related_name='bookings')
    booking_date = models.DateField()
    booking_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-booking_date', '-booking_time']
        
    def __str__(self):
        return f"Booking {self.id} - {self.user.email} - {self.booking_date} {self.booking_time}"
    
    def is_valid_time(self):
        booking_datetime = timezone.make_aware(
            timezone.datetime.combine(self.booking_date, self.booking_time)
        )
        return booking_datetime > timezone.now()
    
    