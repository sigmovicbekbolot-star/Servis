from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg # Орточо рейтинг үчүн кошулду

# ===================
# КОЛДОНУУЧУЛАР
# ===================
class User(AbstractUser):
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('MANAGER', 'Manager'),
        ('USER', 'User'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='USER')
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name='Телефон номери')
    managed_building = models.ForeignKey(
        'Building', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='managers', verbose_name='Жооптуу имарат'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Катталган күнү')

    groups = models.ManyToManyField(Group, related_name='config_user_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='config_user_permissions_set', blank=True)

    def __str__(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return f"{full_name if full_name else self.username} ({self.role})"

# ===================
# КАТЕГОРИЯЛАР
# ===================
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Категория аты")
    icon = models.CharField(max_length=50, help_text="FontAwesome классы", default="fa-tools")
    image = models.ImageField(upload_to='categories/', null=True, blank=True, verbose_name="Категория сүрөтү")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категориялар"

    def __str__(self):
        return self.name

# ===================
# ОБЪЕКТТЕР (ИМАРАТТАР)
# ===================
class Building(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    image = models.ImageField(upload_to='buildings/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# ===================
# КЫЗМАТТАР
# ===================
class Service(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='services')
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='services/', null=True, blank=True, verbose_name="Сервис сүрөтү")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_average_rating(self):
        # aggregate функциясы базадан түз эсептейт, бул абдан ылдам иштейт
        avg_rating = self.reviews.aggregate(Avg('rating'))['rating__avg']
        return avg_rating if avg_rating is not None else 0.0

# ===================
# ЗАКАЗДАР
# ===================
class Order(models.Model):
    STATUS_CHOICES = [
        ('NEW', 'Ожидания'),
        ('IN_PROGRESS', 'В процессе'),
        ('DONE', 'Выполнено'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    building = models.ForeignKey(Building, null=True, blank=True, on_delete=models.SET_NULL)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Заказ #{self.id}"

# ===================
# ОТЗЫВ ЖАНА РЕЙТИНГ (Оңдолгон бөлүм)
# ===================
class Review(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Жылдызча (1-5)"
    )
    comment = models.TextField(verbose_name="Пикир")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывдар"

    def __str__(self):
        return f"{self.user.username} - {self.service.name} ({self.rating}★)"

# ===================
# ТАРЫХ ЖАНА КАРДАРЛАР
# ===================
class OrderHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='history_logs')
    old_status = models.CharField(max_length=50)
    new_status = models.CharField(max_length=50)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    change_date = models.DateTimeField(auto_now_add=True)

class Client(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.phone}"