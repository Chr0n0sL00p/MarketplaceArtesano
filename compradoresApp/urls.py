# compradoresApp/urls.py
from django.urls import path
from . import views

app_name = 'compradores'

urlpatterns = [
    path('login/', views.comprador_login, name='login'),
    path('logout/', views.comprador_logout, name='logout'),

    path('', views.catalog, name='catalog'),  # catálogo principal comprador
    path('inicio/', views.comprador_home, name='inicio'),  # <-- este es el home del comprador

    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/<int:pk>/review/', views.add_review, name='add_review'),
    path('product/<int:pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.favorites_list, name='favorites'),
    path('notifications/', views.notifications_list, name='notifications'),
    path('returns/', views.returns_policy, name='returns'),
    path('product/<int:pk>/order/', views.create_order, name='create_order'),
]

