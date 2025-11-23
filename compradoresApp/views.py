# compradoresApp/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Product, Category, Favorite, Order, Review, Notification
from .forms import CompradorLoginForm, ReviewForm, FilterForm
from django.core.paginator import Paginator
from django.db.models import Q

def comprador_login(request):
    if request.method == "POST":
        form = CompradorLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(request.GET.get('next') or reverse('compradores:catalog'))
    else:
        form = CompradorLoginForm(request)
    return render(request, 'compradoresApp/login.html', {'form': form})

def comprador_logout(request):
    logout(request)
    return redirect('compradores:login')

def catalog(request):
    products = Product.objects.all()

    if request.user.is_authenticated:
        for p in products:
            p.is_favorite = p.favorited_by.filter(user=request.user).exists()
    else:
        for p in products:
            p.is_favorite = False

    return render(request, 'compradoresApp/catalog.html', {
        'products': products
    })


    paginator = Paginator(qs, 12)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    return render(request, 'compradoresApp/catalog.html', {'products': products, 'form': form})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    review_form = ReviewForm()
    is_fav = False
    if request.user.is_authenticated:
        is_fav = Favorite.objects.filter(user=request.user, product=product).exists()
    reviews = product.reviews.filter(active=True).order_by('-created_at')
    return render(request, 'compradoresApp/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'review_form': review_form,
        'is_fav': is_fav
    })

@login_required
def add_review(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            rev = form.save(commit=False)
            rev.product = product
            rev.author = request.user
            rev.save()
            # notificar al artesano
            Notification.objects.create(user=product.artisan, message=f"Tu producto '{product.title}' recibió una nueva reseña.")
            return redirect('compradores:product_detail', pk=product.pk)
    return redirect('compradores:product_detail', pk=product.pk)

@login_required
def toggle_favorite(request, pk):
    product = get_object_or_404(Product, pk=pk)
    fav, created = Favorite.objects.get_or_create(user=request.user, product=product)
    if not created:
        fav.delete()
    return redirect(request.META.get('HTTP_REFERER', 'compradores:catalog'))

@login_required
def favorites_list(request):
    favs = Favorite.objects.filter(user=request.user).select_related('product')
    return render(request, 'compradoresApp/favorites.html', {'favs': favs})

@login_required
def notifications_list(request):
    notifs = Notification.objects.filter(user=request.user).order_by('-created_at')
    # marcar leídas opcional
    return render(request, 'compradoresApp/notifications.html', {'notifications': notifs})

def returns_policy(request):
    # simple page con política
    return render(request, 'compradoresApp/returns_policy.html')

# vista demo para crear pedido básico
@login_required
def create_order(request, pk):
    product = get_object_or_404(Product, pk=pk)
    order = Order.objects.create(buyer=request.user, product=product, quantity=1, status='P')
    Notification.objects.create(user=product.artisan, message=f"Nuevo pedido por '{product.title}' de {request.user.username}")
    return redirect('compradores:catalog')


def comprador_home(request):
    return render(request, 'compradoresApp/home.html')
