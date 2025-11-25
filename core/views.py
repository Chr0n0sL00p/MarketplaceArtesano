from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Q, Avg, ProtectedError
from django.contrib.admin.views.decorators import staff_member_required

from .models import Tienda, Perfil, Producto, Pedido, Categoria, ResenaDeProducto, Favorito, Notificacion
from .forms import TiendaForm, ProductoForm

# --- Vistas Públicas y de Comprador ---

def home(request):
    """Página de inicio principal."""
    return render(request, 'home.html')

def catalogo(request):
    """Muestra todos los productos disponibles con filtros, búsqueda y paginación."""
    productos = Producto.objects.select_related('tienda', 'categoria').all()
    query = request.GET.get('q', '')
    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(tienda__nombre__icontains=query)
        )
    categoria_id = request.GET.get('categoria', '')
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
        try:
            categoria_id = int(categoria_id)
        except ValueError:
            pass
    orden = request.GET.get('orden', '-fecha_creacion')
    if orden == 'precio_asc':
        productos = productos.order_by('precio')
    elif orden == 'precio_desc':
        productos = productos.order_by('-precio')
    elif orden == 'nombre':
        productos = productos.order_by('nombre')
    else:
        productos = productos.order_by('-fecha_creacion')
    paginator = Paginator(productos, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    categorias = Categoria.objects.all()
    context = {
        'page_obj': page_obj,
        'categorias': categorias,
        'query': query,
        'categoria_seleccionada': categoria_id,
        'orden': orden,
    }
    return render(request, 'catalogo_fixed.html', context)

def detalle_producto(request, producto_id):
    """Muestra los detalles de un producto específico."""
    producto = get_object_or_404(Producto, id=producto_id)
    resenas = producto.resenas.filter(activa=True).order_by('-fecha_creacion')
    es_favorito = False
    if request.user.is_authenticated:
        es_favorito = Favorito.objects.filter(usuario=request.user, producto=producto).exists()
    context = {
        'producto': producto,
        'resenas': resenas,
        'es_favorito': es_favorito,
    }
    return render(request, 'detalle_producto.html', context)

# --- Vistas de Autenticación y Registro ---

def login_usuario(request):
    """Maneja el inicio de sesión para todos los usuarios."""
    if request.method == 'POST':
        username = request.POST.get('usuario')
        password = request.POST.get('contraseña')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Bienvenido {user.username}")
            if hasattr(user, 'perfil'):
                if user.perfil.rol == 'artesano':
                    return redirect('mi_tienda')
                elif user.perfil.rol == 'comprador':
                    return redirect('catalogo')
            return redirect('home')
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
            return redirect('login')
    return render(request, 'login.html')

def logout_usuario(request):
    """Cierra la sesión del usuario."""
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('login')

def registro_artesano(request):
    """Registra un nuevo usuario con el rol de Artesano."""
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        email = request.POST.get('email')
        contraseña = request.POST.get('contraseña')
        confirmar_contraseña = request.POST.get('confirmar_contraseña')
        errores = []
        if User.objects.filter(username=usuario).exists():
            errores.append('El nombre de usuario ya está en uso.')
        if User.objects.filter(email=email).exists():
            errores.append('El correo ya está registrado.')
        if contraseña != confirmar_contraseña:
            errores.append('Las contraseñas no coinciden.')
        if errores:
            for error in errores:
                messages.error(request, error)
            return redirect('registro_artesano')
        try:
            validate_password(contraseña)
        except ValidationError as e:
            for error_msg in e.messages:
                messages.error(request, error_msg)
            return redirect('registro_artesano')
        user = User.objects.create_user(username=usuario, email=email, password=contraseña)
        Perfil.objects.create(user=user, rol='artesano')
        messages.success(request, "Registro de artesano exitoso. Ahora puedes iniciar sesión.")
        return redirect('login')
    return render(request, 'registro_artesano.html')

def registro_comprador(request):
    """Registra un nuevo usuario con el rol de Comprador."""
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        email = request.POST.get('email')
        contraseña = request.POST.get('contraseña')
        confirmar_contraseña = request.POST.get('confirmar_contraseña')
        errores = []
        if User.objects.filter(username=usuario).exists():
            errores.append('El nombre de usuario ya está en uso.')
        if User.objects.filter(email=email).exists():
            errores.append('El correo ya está registrado.')
        if contraseña != confirmar_contraseña:
            errores.append('Las contraseñas no coinciden.')
        if errores:
            for error in errores:
                messages.error(request, error)
            return redirect('registro_comprador')
        try:
            validate_password(contraseña)
        except ValidationError as e:
            for error_msg in e.messages:
                messages.error(request, error_msg)
            return redirect('registro_comprador')
        user = User.objects.create_user(username=usuario, email=email, password=contraseña)
        Perfil.objects.create(user=user, rol='comprador')
        messages.success(request, "Registro de comprador exitoso. Ahora puedes iniciar sesión.")
        return redirect('login')
    return render(request, 'registro_comprador.html')

# --- Vistas de Artesanos (Gestión de Tienda y Productos) ---

@login_required
def crear_tienda(request):
    perfil = get_object_or_404(Perfil, user=request.user, rol='artesano')
    if Tienda.objects.filter(artesano=perfil).exists():
        messages.info(request, "Ya tienes una tienda creada.")
        return redirect('mi_tienda')
    if request.method == 'POST':
        form = TiendaForm(request.POST)
        if form.is_valid():
            tienda = form.save(commit=False)
            tienda.artesano = perfil
            tienda.save()
            messages.success(request, "Tienda creada correctamente 🎉")
            return redirect('mi_tienda')
    else:
        form = TiendaForm()
    return render(request, 'crear_tienda.html', {'form': form})

@login_required
def mi_tienda(request):
    perfil = get_object_or_404(Perfil, user=request.user, rol='artesano')
    tienda = Tienda.objects.filter(artesano=perfil).first()
    if not tienda:
        return redirect('crear_tienda')
    productos = tienda.productos.all().order_by('nombre')
    pedidos = Pedido.objects.filter(producto__in=productos).order_by('-fecha_creacion')
    context = {'tienda': tienda, 'productos': productos, 'pedidos': pedidos}
    return render(request, 'mi_tienda.html', context)

@login_required
def crear_producto(request):
    tienda = get_object_or_404(Tienda, artesano__user=request.user)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save(commit=False)
            producto.tienda = tienda
            producto.save()
            messages.success(request, "Producto agregado correctamente 🎉")
            return redirect('mi_tienda')
    else:
        form = ProductoForm()
    return render(request, 'crear_producto.html', {'form': form})

@login_required
def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, tienda__artesano__user=request.user)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto actualizado correctamente 🎉")
            return redirect('mi_tienda')
    else:
        form = ProductoForm(instance=producto)
    context = {'form': form, 'producto': producto}
    return render(request, 'editar_producto.html', context)

@login_required
def eliminar_producto(request, producto_id):
    """Elimina un producto con confirmación (solo POST)."""
    producto = get_object_or_404(Producto, id=producto_id, tienda__artesano__user=request.user)
    if request.method == 'POST':
        nombre_producto = producto.nombre
        try:
            producto.delete()
            messages.success(request, f"Producto '{nombre_producto}' eliminado correctamente 🗑️")
        except ProtectedError:
            messages.error(request, f"No se puede eliminar '{nombre_producto}' porque tiene pedidos asociados.")
        return redirect('mi_tienda')
    return render(request, 'confirmar_eliminar_producto.html', {'producto': producto})

@login_required
def simular_pedido(request, producto_id):
    """Crea un pedido verificando stock disponible."""
    producto = get_object_or_404(Producto, id=producto_id)
    if producto.stock < 1:
        messages.error(request, f"❌ Lo sentimos, {producto.nombre} está agotado.")
        return redirect('detalle_producto', producto_id=producto_id)
    Pedido.objects.create(producto=producto, comprador=request.user, cantidad=1)
    producto.stock -= 1
    producto.save()
    Notificacion.objects.create(
        usuario=producto.tienda.artesano.user,
        mensaje=f"Nuevo pedido de {producto.nombre} por {request.user.username}"
    )
    messages.success(request, f"✅ Pedido de {producto.nombre} realizado exitosamente.")
    return redirect('mis_pedidos')

@login_required
def mis_pedidos(request):
    """Muestra los pedidos del comprador."""
    pedidos = Pedido.objects.filter(comprador=request.user).select_related('producto__tienda').order_by('-fecha_creacion')
    return render(request, 'mis_pedidos.html', {'pedidos': pedidos})

# --- Vistas de Favoritos ---

@login_required
def toggle_favorito(request, producto_id):
    """Agrega o quita un producto de favoritos."""
    producto = get_object_or_404(Producto, id=producto_id)
    favorito = Favorito.objects.filter(usuario=request.user, producto=producto).first()
    if favorito:
        favorito.delete()
        messages.info(request, f"Quitaste {producto.nombre} de tus favoritos.")
    else:
        Favorito.objects.create(usuario=request.user, producto=producto)
        messages.success(request, f"Agregaste {producto.nombre} a tus favoritos ❤️")
    return redirect('detalle_producto', producto_id=producto_id)

@login_required
def mis_favoritos(request):
    """Muestra los productos favoritos del usuario."""
    favoritos = Favorito.objects.filter(usuario=request.user).select_related('producto__tienda')
    return render(request, 'mis_favoritos.html', {'favoritos': favoritos})

# --- Vistas de Notificaciones ---

@login_required
def mis_notificaciones(request):
    """Muestra las notificaciones del usuario."""
    notificaciones = Notificacion.objects.filter(usuario=request.user).order_by('-fecha_creacion')
    notificaciones.filter(leida=False).update(leida=True)
    return render(request, 'mis_notificaciones.html', {'notificaciones': notificaciones})

# --- Vista de Administración ---

@login_required
@staff_member_required
def admin_dashboard(request):
    """Muestra un panel de administración con estadísticas del sitio."""
    total_usuarios = User.objects.count()
    total_productos = Producto.objects.count()
    total_tiendas = Tienda.objects.count()
    tiendas_pendientes = Tienda.objects.filter(aprobada=False).count()
    ultimos_pedidos = Pedido.objects.order_by('-fecha_creacion')[:5]
    ultimos_usuarios = User.objects.order_by('-date_joined')[:5]
    context = {
        'total_usuarios': total_usuarios,
        'total_productos': total_productos,
        'total_tiendas': total_tiendas,
        'tiendas_pendientes': tiendas_pendientes,
        'ultimos_pedidos': ultimos_pedidos,
        'ultimos_usuarios': ultimos_usuarios,
    }
    return render(request, 'admin.html', context)