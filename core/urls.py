"""
URL configuration for proyectoIntegrado project.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Rutas Principales y de Catálogo
    path('', views.home, name='home'),
    path('catalogo/', views.catalogo, name='catalogo'),
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),

    # Autenticación
    path('login/', views.login_usuario, name='login'),
    path('logout/', views.logout_usuario, name='logout'),
    path('registro/artesano/', views.registro_artesano, name='registro_artesano'),
    path('registro/comprador/', views.registro_comprador, name='registro_comprador'),
    
    # Vistas de Artesano y Gestión de Tienda
    path('tienda/crear/', views.crear_tienda, name='crear_tienda'),
    path('tienda/mi_tienda/', views.mi_tienda, name='mi_tienda'),
    path('tienda/producto/crear/', views.crear_producto, name='crear_producto'),
    path('tienda/producto/<int:producto_id>/editar/', views.editar_producto, name='editar_producto'),
    path('tienda/producto/<int:producto_id>/eliminar/', views.eliminar_producto, name='eliminar_producto'),
    
    # Pedidos
    path('pedido/<int:producto_id>/', views.simular_pedido, name='simular_pedido'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    
    # Favoritos
    path('favorito/toggle/<int:producto_id>/', views.toggle_favorito, name='toggle_favorito'),
    path('mis-favoritos/', views.mis_favoritos, name='mis_favoritos'),
    
    # Notificaciones
    path('notificaciones/', views.mis_notificaciones, name='mis_notificaciones'),
    
    # Admin
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
