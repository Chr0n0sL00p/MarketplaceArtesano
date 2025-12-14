from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone



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
    documento_identidad = models.FileField(upload_to='documentos_identidad/', blank=True, null=True)
    verificado = models.BooleanField(default=False)

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
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=1)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

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
        ('CA', 'Cancelado'),
        ('R', 'Rechazado'),
    )
    comprador = models.ForeignKey(User, related_name='pedidos', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=2, choices=ESTADOS, default='P')


    def __str__(self):
        return f"Pedido #{self.id} - {self.producto.nombre}"

class ResenaDeProducto(models.Model):
    producto = models.ForeignKey(Producto, related_name='resenas', on_delete=models.CASCADE)
    autor = models.ForeignKey(User, related_name='resenas_realizadas', on_delete=models.CASCADE)
    calificacion = models.PositiveSmallIntegerField(default=5)
    comentario = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=True)
    aprobada = models.BooleanField(default=False)
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
    TIPO_CHOICES = [
        ('pedido', 'Pedido'),
        ('reseña', 'Reseña'),
        ('general', 'General'),
    ]
    usuario = models.ForeignKey(User, related_name='notificaciones', on_delete=models.CASCADE)
    mensaje = models.CharField(max_length=255)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    leida = models.BooleanField(default=False)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='general')
    url = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"Notificación para {self.usuario.username} — {self.mensaje[:30]}"


# --- NUEVOS MODELOS PARA EL MÓDULO ADMINISTRATIVO Y COMUNICACIÓN ---

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class SoporteTicket(models.Model):
    ESTADOS = (
        ('abierto', 'Abierto'),
        ('en_proceso', 'En Proceso'),
        ('cerrado', 'Cerrado'),
    )
    usuario = models.ForeignKey(User, related_name='tickets_soporte', on_delete=models.CASCADE)
    asunto = models.CharField(max_length=200)
    mensaje = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='abierto')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    respuesta_admin = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Ticket #{self.id} - {self.asunto} ({self.get_estado_display()})"


class Conversacion(models.Model):
    participante_1 = models.ForeignKey(User, related_name='conversaciones_p1', on_delete=models.CASCADE)
    participante_2 = models.ForeignKey(User, related_name='conversaciones_p2', on_delete=models.CASCADE)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('participante_1', 'participante_2')

    def __str__(self):
        return f"Chat: {self.participante_1.username} y {self.participante_2.username}"


class MensajeChat(models.Model):
    conversacion = models.ForeignKey(Conversacion, related_name='mensajes', on_delete=models.CASCADE)
    remitente = models.ForeignKey(User, related_name='mensajes_enviados', on_delete=models.CASCADE)
    texto = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)

    def __str__(self):
        return f"Mensaje de {self.remitente.username} en {self.conversacion}"


class ReporteAbuso(models.Model):
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('revisado', 'Revisado'),
        ('desestimado', 'Desestimado'),
    )
    reportante = models.ForeignKey(User, related_name='reportes_realizados', on_delete=models.CASCADE)
    motivo = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')

    # Generic relation to target Product or Tienda (or User if needed)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"Reporte de {self.reportante.username} - {self.get_estado_display()}"


class SeguirTienda(models.Model):
    usuario = models.ForeignKey(User, related_name='tiendas_seguidas', on_delete=models.CASCADE)
    tienda = models.ForeignKey(Tienda, related_name='seguidores_tienda', on_delete=models.CASCADE)
    fecha_seguimiento = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'tienda')

    def __str__(self):
        return f"{self.usuario.username} sigue a {self.tienda.nombre}"
