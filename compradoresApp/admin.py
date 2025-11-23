# compradoresApp/admin.py
from django.contrib import admin
from .models import Category, Product, Order, Review, Favorite, Notification

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Review)
admin.site.register(Favorite)
admin.site.register(Notification)
