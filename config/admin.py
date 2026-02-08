from django.contrib import admin
from .models import User, Building, Service, Order, OrderHistory, Client, Category, Review


admin.site.register(Review)
admin.site.register(Category)
admin.site.register(Building)
admin.site.register(Service)
admin.site.register(Order)
admin.site.register(OrderHistory)
admin.site.register(Client)