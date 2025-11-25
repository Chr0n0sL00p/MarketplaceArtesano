from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# --- Modelos Base de Usuarios y Tiendas (Conservados y Mejorados) ---

class Perfil(models.Model):
    ROLES = [
        ('artesano', 'Artesano'),
        ('comprador', 'Comprador'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol = models.CharField(max_length=20, choices=ROLES)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    correo_validado = models.BooleanField(default=False)
    telefono_validado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} ({self.rol})"

class Tienda(models.Model):
    artesano = models.OneToOneField(Perfil, on_delete=models.CASCADE, limit_choices_to={'rol': 'artesano'})
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    ubicacion = models.CharField(max_length=100)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=True)
    aprobada = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre

# --- Modelos de E-Commerce (Fusionados y Estandarizados desde compradoresApp) ---

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    class Meta:
        verbose_name = "categoría"
        verbose_name_plural = "categorías"

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE, related_name='productos')
    categoria = models.ForeignKey(Categoria, related_name='productos', on_delete=models.SET_NULL, null=True, blank=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2) # CORRECTO: Usar DecimalField para precios
    stock = models.IntegerField(default=1)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

    def calificacion_promedio(self):
        qs = self.resenas.filter(activa=True)
        if not qs.exists():
            return 0
        return round(sum(r.calificacion for r in qs) / qs.count(), 1)


class Pedido(models.Model):
    ESTADOS = (
        ('P', 'Pendiente'),
        ('C', 'Completado'),
        ('R', 'Rechazado'),
    )
    comprador = models.ForeignKey(User, related_name='pedidos', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT) # Usar PROTECT es buena idea para no borrar pedidos si se borra un producto
    cantidad = models.PositiveIntegerField(default=1)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=1, choices=ESTADOS, default='P')
    # NOTA: Este modelo es simple. Un sistema real usaría un modelo 'Pedido' y 'DetallePedido' para soportar múltiples productos en una orden.

    def __str__(self):
        return f"Pedido #{self.id} - {self.producto.nombre}"

class ResenaDeProducto(models.Model):
    producto = models.ForeignKey(Producto, related_name='resenas', on_delete=models.CASCADE)
    autor = models.ForeignKey(User, related_name='resenas_realizadas', on_delete=models.CASCADE)
    calificacion = models.PositiveSmallIntegerField(default=5)
    comentario = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=True)
    respuesta_artesano = models.TextField(blank=True)
    fecha_respuesta = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "reseña de producto"
        verbose_name_plural = "reseñas de productos"
        unique_together = ('producto', 'autor')

    def responder(self, texto):
        self.respuesta_artesano = texto
        self.fecha_respuesta = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.autor.username} - {self.producto.nombre} ({self.calificacion})"

class ResenaDeTienda(models.Model):
    tienda = models.ForeignKey(Tienda, related_name='resenas', on_delete=models.CASCADE)
    autor = models.ForeignKey(User, related_name='resenas_tienda', on_delete=models.CASCADE)
    calificacion = models.IntegerField()
    comentario = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    aprobada = models.BooleanField(default=False)

    class Meta:
        verbose_name = "reseña de tienda"
        verbose_name_plural = "reseñas de tiendas"
        unique_together = ('tienda', 'autor')

    def __str__(self):
        return f"Reseña de {self.autor.username} en {self.tienda.nombre}"


class Favorito(models.Model):
    usuario = models.ForeignKey(User, related_name='favoritos', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, related_name='seguidores', on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'producto')

    def __str__(self):
        return f"{self.usuario.username} ► {self.producto.nombre}"

class Notificacion(models.Model):
    usuario = models.ForeignKey(User, related_name='notificaciones', on_delete=models.CASCADE)
    mensaje = models.CharField(max_length=255)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    leida = models.BooleanField(default=False)

    def __str__(self):
        return f"Notificación para {self.usuario.username} — {self.mensaje[:30]}"