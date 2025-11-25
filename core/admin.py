from django.contrib import admin
from .models import Perfil, Tienda, Producto, Categoria, Pedido, ResenaDeProducto, Favorito, Notificacion

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'rol', 'telefono', 'ciudad')
    search_fields = ('user__username', 'rol', 'ciudad')


@admin.register(Tienda)
class TiendaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'artesano', 'ubicacion', 'fecha_creacion', 'aprobada')
    search_fields = ('nombre', 'artesano__user__username', 'ubicacion')
    list_filter = ('aprobada', 'activa')


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tienda', 'precio', 'stock', 'categoria', 'fecha_creacion')
    search_fields = ('nombre', 'tienda__nombre', 'categoria__nombre')
    list_filter = ('categoria', 'fecha_creacion')


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug')
    search_fields = ('nombre',)
    prepopulated_fields = {'slug': ('nombre',)}


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'comprador', 'producto', 'cantidad', 'estado', 'fecha_creacion')
    search_fields = ('comprador__username', 'producto__nombre')
    list_filter = ('estado', 'fecha_creacion')


@admin.register(ResenaDeProducto)
class ResenaDeProductoAdmin(admin.ModelAdmin):
    list_display = ('producto', 'autor', 'calificacion', 'activa', 'fecha_creacion')
    search_fields = ('producto__nombre', 'autor__username')
    list_filter = ('activa', 'calificacion', 'fecha_creacion')


@admin.register(Favorito)
class FavoritoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'producto', 'fecha_creacion')
    search_fields = ('usuario__username', 'producto__nombre')


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'mensaje', 'leida', 'fecha_creacion')
    search_fields = ('usuario__username', 'mensaje')
    list_filter = ('leida', 'fecha_creacion')
