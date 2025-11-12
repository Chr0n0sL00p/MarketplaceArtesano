from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from .models import Tienda, Perfil, Producto, Venta
from django.shortcuts import get_object_or_404
# Página principal
def home(request):
    return render(request, 'home.html')


# Login 
def login_usuario(request):
    if request.method == 'POST':
        username = request.POST.get('usuario')
        password = request.POST.get('contraseña')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Bienvenido {user.username}")
            return HttpResponseRedirect(reverse('home'))
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
            return HttpResponseRedirect(reverse('login'))

    return render(request, 'login.html')




# Cerrar sesión
def logout_usuario(request):
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return HttpResponseRedirect(reverse('login'))


# Registro de artesano
def registro_artesano(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        email = request.POST.get('email')
        contraseña = request.POST.get('contraseña')

        # Validar que el correo no exista
        if User.objects.filter(email=email).exists():
            messages.error(request, "El correo ya está registrado.")
            return HttpResponseRedirect(reverse('registro_artesano'))

        # Crear usuario base de Django (parámetros correctos)
        user = User.objects.create_user(username=usuario, email=email, password=contraseña)

        # Crear perfil asociado al usuario
        Perfil.objects.create(user=user, rol='artesano')

        messages.success(request, "Registro exitoso. Ahora puedes iniciar sesión.")
        return HttpResponseRedirect(reverse('login'))

    return render(request, 'registro_artesano.html')



# Crear tienda formulario y guardado
def crear_tienda(request):
    perfil = Perfil.objects.get(user=request.user)
    tienda_existente = Tienda.objects.filter(artesano=perfil).first()

    # Si ya tiene una tienda, lo redirigimos directamente
    if tienda_existente:
        messages.info(request, "Ya tienes una tienda creada.")
        return HttpResponseRedirect(reverse('mi_tienda'))

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        ubicacion = request.POST.get('ubicacion')

        # Crear la tienda asociada al artesano
        Tienda.objects.create(
            artesano=perfil,
            nombre=nombre,
            descripcion=descripcion,
            ubicacion=ubicacion
        )

        messages.success(request, "Tienda creada correctamente 🎉")
        return HttpResponseRedirect(reverse('mi_tienda'))

    return render(request, 'crear_tienda.html')


# Mi Tienda
def mi_tienda(request):
    perfil = Perfil.objects.get(user=request.user)
    tienda = Tienda.objects.filter(artesano=perfil).first()

    if not tienda:
        messages.info(request, "Aún no tienes una tienda. ¡Crea una ahora!")
        return render(request, 'crear_tienda.html')

    # Productos del artesano
    productos = tienda.producto_set.all()

    # Ventas asociadas a esos productos
    ventas = Venta.objects.filter(producto__in=productos).order_by('-fecha')

    # Notificaciones (ventas no notificadas)
    notificaciones = Venta.objects.filter(producto__in=productos, notificado=False).count()

    context = {
        'tienda': tienda,
        'productos': productos,
        'ventas': ventas,
        'notificaciones': notificaciones
    }
    return render(request, 'mi_tienda.html', context)


# crear producto
def crear_producto(request):
    perfil = Perfil.objects.get(user=request.user)
    tienda = Tienda.objects.filter(artesano=perfil).first()

    if not tienda:
        messages.error(request, "Primero debes crear tu tienda antes de agregar productos.")
        return HttpResponseRedirect(reverse('mi_tienda'))

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        precio = request.POST.get('precio')
        categoria = request.POST.get('categoria')
        descripcion = request.POST.get('descripcion')
        imagen = request.FILES.get('imagen')

        Producto.objects.create(
            tienda=tienda,
            nombre=nombre,
            precio=precio,
            categoria=categoria,
            descripcion=descripcion,
            imagen=imagen
        )

        messages.success(request, "Producto agregado correctamente 🎉")
        return HttpResponseRedirect(reverse('mi_tienda'))

    return render(request, 'crear_producto.html')



# Editar producto
def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, tienda__artesano__user=request.user)

    if request.method == 'POST':
        producto.nombre = request.POST.get('nombre')
        producto.precio = request.POST.get('precio')
        producto.categoria = request.POST.get('categoria')
        producto.descripcion = request.POST.get('descripcion')

        # Si se sube una nueva imagen
        if 'imagen' in request.FILES:
            producto.imagen = request.FILES['imagen']

        producto.save()
        messages.success(request, "Producto actualizado correctamente 🎉")
        return HttpResponseRedirect(reverse('mi_tienda'))

    context = {'producto': producto}
    return render(request, 'editar_producto.html', context)


# Eliminar producto
def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, tienda__artesano__user=request.user)
    producto.delete()
    messages.success(request, "Producto eliminado correctamente 🗑️")
    return HttpResponseRedirect(reverse('mi_tienda'))

# Simulador de ventas 
def simular_venta(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    Venta.objects.create(producto=producto, comprador=request.user)
    messages.success(request, f"✅ Simulaste la venta de {producto.nombre}.")
    return HttpResponseRedirect(reverse('mi_tienda'))
