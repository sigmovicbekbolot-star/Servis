from django.db.models import Q, Avg  # Avg кошулду - орточо рейтинг үчүн
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, permissions, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import PermissionDenied

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

# Моделдер жана Сериализаторлор
from .models import User, Building, Service, Order, OrderHistory, Client, Category, Review
from .serializers import (
    UserSerializer, BuildingSerializer, ServiceSerializer,
    OrderSerializer, OrderHistorySerializer, RegisterSerializer
)


# ===================
# 1. API РЕГИСТРАЦИЯ
# ===================
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


# ===================
# РЕГИСТРАЦИЯ (HTML)
# ===================
class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.role = 'USER'
            user.save()
            messages.success(request, "Каттоо ийгиликтүү өттү! Эми кириңиз.")
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


# ===================
# ФОРМАЛАР
# ===================
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['service', 'building', 'status']


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']


# ===================
# HTML VIEWS
# ===================
@login_required
def home(request):
    categories = Category.objects.all()
    # .prefetch_related('reviews') кошуу базага болгон сурамды азайтат жана маалыматты тез алат
    services = Service.objects.all().prefetch_related('reviews')

    search_query = request.GET.get('search')
    if search_query:
        services = services.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))

    category_id = request.GET.get('category')
    if category_id:
        services = services.filter(category_id=category_id)

    return render(request, 'home.html', {'categories': categories, 'services': services})


@login_required
def update_order_status(request, pk, status):
    order = get_object_or_404(Order, pk=pk)
    if request.user.role == 'MANAGER' and order.building == request.user.managed_building:
        old_status = order.status
        order.status = status
        order.save()
        OrderHistory.objects.create(order=order, old_status=old_status, new_status=status, changed_by=request.user)
        messages.success(request, f"Заказ статусу {status} деп өзгөртүлдү!")
    elif request.user.role == 'ADMIN':
        order.status = status
        order.save()
        messages.success(request, "Админ катары статус өзгөртүлдү!")
    else:
        messages.error(request, "Сизге бул аракетке уруксат жок!")
    return redirect('dashboard')


# ---------------------------------------------------------
# ЖАҢЫЛАНГАН SERVICE_DETAIL (Пикир калтыруу логикасы менен)
# ---------------------------------------------------------
@login_required
def service_detail(request, pk):
    # Кызматты базадан издөө
    service = get_object_or_404(Service, pk=pk)
    # Ушул кызматка тиешелүү пикирлерди алуу
    reviews = service.reviews.all().order_by('-created_at')

    if request.method == "POST":
        # Формадан маалыматты алуу
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        if rating and comment:
            # Маалыматты базага сактоо
            Review.objects.create(
                service=service,
                user=request.user,
                rating=int(rating),
                comment=comment
            )
            messages.success(request, "Пикириңиз ийгиликтүү кошулду!")
            return redirect('service_detail', pk=service.id)

    # reviews маалыматын контекстке кошууну унутпа!
    return render(request, 'service_detail.html', {
        'service': service,
        'reviews': reviews  # Мына ушул жер маанилүү!
    })


@login_required
def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)
    return render(request, 'client_detail.html', {'client': client})


@login_required
def client_edit(request, pk):
    client = get_object_or_404(Client, pk=pk)
    return render(request, 'client_form.html', {'client': client})


@login_required
def client_create(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        if first_name and phone:
            Client.objects.create(first_name=first_name, last_name=last_name, phone=phone, email=email)
            messages.success(request, "Жаңы кардар ийгиликтүү кошулду!")
            return redirect('clients')
    return render(request, 'client_form.html')


@login_required
def dashboard(request):
    user = request.user
    if user.role == 'ADMIN':
        orders = Order.objects.all()
    elif user.role == 'MANAGER':
        orders = Order.objects.filter(building=user.managed_building)
    else:
        orders = Order.objects.filter(user=user)
    return render(request, 'orders.html', {'orders': orders})


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    history = OrderHistory.objects.filter(order=order).order_by('-change_date')
    return render(request, 'order_detail.html', {'order': order, 'history': history})


@login_required
def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == "POST":
        order_id = order.id
        order.delete()
        messages.warning(request, f"#{order_id} заказы өчүрүлдү!")
        return redirect('dashboard')
    return render(request, 'order_confirm_delete.html', {'order': order})


@login_required
def order_edit(request, pk):
    order = get_object_or_404(Order, pk=pk)
    old_status = order.status
    if request.method == "POST":
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            updated_order = form.save()
            if old_status != updated_order.status:
                OrderHistory.objects.create(order=updated_order, old_status=old_status, new_status=updated_order.status,
                                            changed_by=request.user)
            messages.success(request, "Заказ ийгиликтүү жаңыланды!")
            return redirect('order_detail', pk=order.id)
    else:
        form = OrderForm(instance=order)
    return render(request, 'order_form.html', {'form': form, 'order': order})


@login_required
def create_order(request):
    services = Service.objects.all()
    buildings = Building.objects.all()
    selected_service_id = request.GET.get('service')
    if request.method == 'POST':
        service_id = request.POST.get('service')
        building_id = request.POST.get('building')
        comment = request.POST.get('comment', '')
        from django.utils import timezone
        now = timezone.now()
        Order.objects.create(
            user=request.user,
            service=get_object_or_404(Service, id=service_id),
            building=get_object_or_404(Building, id=building_id),
            date=request.POST.get('date') or now.date(),
            time=request.POST.get('time') or now.time(),
            comment=comment,
            status='NEW'
        )
        messages.success(request, "Жаңы заказ ийгиликтүү түзүлдү!")
        return redirect('dashboard')
    return render(request, 'create_order.html',
                  {'services': services, 'buildings': buildings, 'selected_service_id': selected_service_id})


@login_required
def clients_view(request):
    clients = Client.objects.all()
    return render(request, 'clients.html', {'clients': clients})


@login_required
def buildings_view(request):
    buildings = Building.objects.all()
    return render(request, 'buildings.html', {'buildings': buildings})


# ===================
# 2. API ROOT
# ===================
@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
    return Response({
        '0. Registration': reverse('register', request=request, format=format),
        '1. Имараттар': reverse('building-list', request=request, format=format),
        '2. Менеджерлер': reverse('manager-list', request=request, format=format),
        '3. Кызматтар': reverse('service-list', request=request, format=format),
        '4. Кардарлар': reverse('client-list', request=request, format=format),
        '5. Заказдар': reverse('order-list', request=request, format=format),
        '6. Тарых': reverse('orderhistory-list', request=request, format=format),
    })


# ===================
# API VIEWSETS
# ===================
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class ManagerViewSet(UserViewSet):
    def get_queryset(self):
        return User.objects.filter(role='MANAGER')


class ClientViewSet(UserViewSet):
    def get_queryset(self):
        return User.objects.filter(role='USER')


class BuildingViewSet(viewsets.ModelViewSet):
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer
    permission_classes = [permissions.IsAuthenticated]


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN' or user.is_staff:
            return Order.objects.all()
        if user.role == 'MANAGER':
            return Order.objects.filter(building=user.managed_building)
        return Order.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, status='NEW')

    def perform_update(self, serializer):
        instance = self.get_object()
        old_status = instance.status
        new_order = serializer.save()
        if old_status != new_order.status:
            OrderHistory.objects.create(order=new_order, old_status=old_status, new_status=new_order.status)


class OrderHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OrderHistory.objects.all()
    serializer_class = OrderHistorySerializer
    permission_classes = [permissions.IsAuthenticated]