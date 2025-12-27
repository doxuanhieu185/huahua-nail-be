from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, NailSample, Booking

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'username', 'role', 'is_staff', 'is_active','phone_number','profile_picture')
    list_filter = ('role', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Persional info', {'fields': ('phone_number', 'profile_picture')}),
        ('Permissions', {'fields': ('role', 'is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'role', 'is_staff', 'is_active', 'phone_number', 'profile_picture')}
        ),
    )
    search_fields = ('email', 'username',)
    ordering = ('email',)

admin.site.register(CustomUser, CustomUserAdmin)


class NailSampleAdmin(admin.ModelAdmin):
    list_display = ('id', 'detail', 'price', 'created_at')
    search_fields = ('detail',)
    list_filter = ('price', 'created_at')

admin.site.register(NailSample, NailSampleAdmin)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'nail_sample', 'booking_date', 'booking_time', 'status', 'created_at')
    list_filter = ('status', 'booking_date')
    search_fields = ('user__email', 'nail_sample__name')
    ordering = ('-booking_date', '-booking_time')
    date_hierarchy = 'booking_date'
    list_editable = ('status',)  # Cho phép chỉnh sửa trạng thái trực tiếp trên danh sách booking
    readonly_fields = ('created_at', 'updated_at')  # Chỉ đọc các trường này

    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('user', 'nail_sample', 'booking_date', 'booking_time', 'status')
        }),
        ('Ghi chú', {
            'fields': ('notes',),
            'classes': ('collapse',)  # Thu gọn phần này
        }),
        ('Thông tin hệ thống', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Thu gọn phần này
        }),
    )

    def nail_sample_name(self, obj):
        return obj.nail_sample.name if obj.nail_sample else "Không có mẫu"
    nail_sample_name.short_description = "Nail Sample"