from rest_framework import serializers
from .models import User, Building, Service, Order, OrderHistory


# ==========================================
# 1. ЖАҢЫ: КАТТОО ҮЧҮН SERIALIZER
# ==========================================
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    phone = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('phone', 'first_name', 'last_name', 'email', 'password')

    # Телефон номерин текшерүү (Validation)
    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Бул телефон номери менен колдонуучу мурун катталган!")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['phone'],
            phone=validated_data['phone'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role='USER'
        )
        return user


# ==========================================
# 2. СЕНИН КОДУҢ (Өзгөртүүсүз сакталды + баа кошулду)
# ==========================================
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'phone')
        read_only_fields = ('id',)


class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = '__all__'


class ServiceSerializer(serializers.ModelSerializer):
    # Бааны $ менен чыгаруучу талаа
    price_display = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = '__all__'

    def get_price_display(self, obj):
        return f"${obj.price}"


class OrderSerializer(serializers.ModelSerializer):
    building = BuildingSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    service = ServiceSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'date', 'time', 'status', 'comment', 'created_at', 'user', 'service', 'building')


class OrderHistorySerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(read_only=True)
    old_status = serializers.SerializerMethodField()
    new_status = serializers.SerializerMethodField()

    class Meta:
        model = OrderHistory
        fields = ('id', 'order', 'old_status', 'new_status', 'change_date')

    STATUS_DISPLAY = {
        'NEW': 'Ожидания',
        'PENDING': 'Ожидания',
        'IN_PROGRESS': 'В процессе',
        'DONE': 'Выполнено',
    }

    def get_old_status(self, obj):
        return self.STATUS_DISPLAY.get(obj.old_status, obj.old_status)

    def get_new_status(self, obj):
        return self.STATUS_DISPLAY.get(obj.new_status, obj.new_status)