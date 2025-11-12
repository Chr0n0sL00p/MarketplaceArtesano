from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User

# PERFIL DE USUARIO
class Perfil(models.Model):
    ROLES = [
        ('artesano', 'Artesano'),
        ('comprador', 'Comprador'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.CharField(max_length=20, choices=ROLES)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    verificado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} ({self.rol})"


# TIENDA DEL ARTESANO
class Tienda(models.Model):
    artesano = models.ForeignKey(Perfil, on_delete=models.CASCADE, limit_choices_to={'rol': 'artesano'})
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    ubicacion = models.CharField(max_length=100)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre


# PRODUCTOS
class Producto(models.Model):
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.CharField(max_length=100)
    imagen = models.URLField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)

    def __str__(self):
        return self.nombre

# VENTAS
class Venta(models.Model):
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    comprador = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    notificado = models.BooleanField(default=False)

    def __str__(self):
        return f"Venta de {self.producto.nombre} a {self.comprador.username}"
