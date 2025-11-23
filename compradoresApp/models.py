# compradoresApp/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    artisan = models.ForeignKey(User, related_name='products', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=120, blank=True)  # ciudad / región
    image = models.ImageField(upload_to='products/', null=True, blank=True)  # requiere pillow
    created_at = models.DateTimeField(auto_now_add=True)
    stock = models.IntegerField(default=1)

    def average_rating(self):
        qs = self.reviews.filter(active=True)
        if not qs.exists():
            return 0
        return round(sum(r.rating for r in qs)/qs.count(), 1)

    def __str__(self):
        return self.title

class Order(models.Model):
    STATUS_CHOICES = (
        ('P', 'Pendiente'),
        ('C', 'Completado'),
        ('R', 'Rechazado'),
    )
    buyer = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    # puedes añadir direccion, pago, etc.

    def __str__(self):
        return f"Pedido #{self.id} - {self.product.title}"

class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(default=5)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    artisan_response = models.TextField(blank=True)  # respuesta visible del artesano
    response_created_at = models.DateTimeField(null=True, blank=True)

    def respond(self, text):
        self.artisan_response = text
        self.response_created_at = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.author.username} - {self.product.title} ({self.rating})"

class Favorite(models.Model):
    user = models.ForeignKey(User, related_name='favorites', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='favorited_by', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} ► {self.product.title}"

class Notification(models.Model):
    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notif to {self.user.username} — {self.message[:30]}"
