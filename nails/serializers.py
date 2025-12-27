from rest_framework import serializers
from .models import CustomUser, NailSample, Booking
from django.utils import timezone

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'role', 'phone_number', 'profile_picture')
        read_only_fields = ('id','role', 'email')

class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'phone_number')
        
class UpdateProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('profile_picture',)

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'password', 'password_confirm')
    
    def validate(self, attrs):
        # Kiểm tra không trả ra lỗi mà chỉ đánh dấu các trường không hợp lệ
        attrs['valid'] = True
        attrs['errors'] = {}
        
        if attrs['password'] != attrs['password_confirm']:
            attrs['valid'] = False
            attrs['errors']['password'] = "Mật khẩu xác nhận không khớp"
        
        if CustomUser.objects.filter(email=attrs['email']).exists():
            attrs['valid'] = False
            attrs['errors']['email'] = "Email này đã được sử dụng"
        
        if CustomUser.objects.filter(username=attrs['username']).exists():
            attrs['valid'] = False
            attrs['errors']['username'] = "Tên người dùng này đã được sử dụng"
            
        return attrs
    
    def create(self, validated_data):
        # Loại bỏ các trường không cần thiết cho việc tạo user
        validated_data.pop('password_confirm', None)
        validated_data.pop('valid', None)
        validated_data.pop('errors', None)
        
        # Tạo user
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']
        )
        
        return user

class NailSampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = NailSample
        fields = '__all__'
        

class BookingSerializer(serializers.ModelSerializer):
    nail_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = ('id', 'user', 'nail_sample', 'nail_name', 'booking_date', 'booking_time', 'status', 'notes', 'created_at')
        read_only_fields = ('user', 'status', 'created_at')
    
    def get_nail_name(self, obj):
        if obj.nail_sample:
            return f"Mẫu nail: {obj.nail_sample.id} - {obj.nail_sample.price}"
        return None
    
    def validate(self, data):
       
        booking_datetime = timezone.make_aware(
            timezone.datetime.combine(data['booking_date'], data['booking_time'])
        )
        if booking_datetime < timezone.now():
            raise serializers.ValidationError("Không thể đặt lịch trong quá khứ.")
        if data['booking_time'].hour < 8 or data['booking_time'].hour >= 20:
            raise serializers.ValidationError("Giờ đặt lịch phải từ 8:00 đến 20:00.")
        
        bookings = Booking.objects.filter(
            booking_date=data['booking_date'],
            booking_time=data['booking_time'],
            status__in=['pending', 'confirmed']
        )
        if self.instance:
            bookings = bookings.exclude(pk=self.instance.pk)
            
        if bookings.exists():
            raise serializers.ValidationError("Khung giờ này đã được đặt. Vui lòng chọn thời gian khác.")
            
        return data