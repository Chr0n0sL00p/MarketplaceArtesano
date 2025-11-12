from django.contrib import admin
from .models import Perfil, Tienda, Producto

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'rol', 'telefono', 'ciudad', 'verificado')
    search_fields = ('user__username', 'rol', 'ciudad')


@admin.register(Tienda)
class TiendaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'artesano', 'ubicacion', 'fecha_creacion')
    search_fields = ('nombre', 'artesano__user__username', 'ubicacion')


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tienda', 'precio', 'categoria', 'fecha_creacion')
    search_fields = ('nombre', 'categoria', 'tienda__nombre')
