from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Q, Avg, ProtectedError
from django.contrib.admin.views.decorators import staff_member_required
import logging
from django.db.models.deletion import ProtectedError
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
logger = logging.getLogger(__name__)

from .models import Tienda, Perfil, Producto, Pedido, Categoria, ResenaDeProducto, Favorito, Notificacion, SoporteTicket, Conversacion, MensajeChat, ReporteAbuso, SeguirTienda
from .forms import TiendaForm, ProductoForm, ResenaDeProductoForm, SoporteTicketForm, MensajeChatForm, ReporteAbusoForm



def home(request):
    return render(request, 'home.html')

def catalogo(request):
    productos = Producto.objects.select_related('tienda', 'categoria').filter(activo=True)
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
    producto = get_object_or_404(Producto, id=producto_id)
    resenas = producto.resenas.filter(activa=True).order_by('-fecha_creacion')
    es_favorito = False
    if request.user.is_authenticated:
        es_favorito = Favorito.objects.filter(usuario=request.user, producto=producto).exists()
    
    resena_form = ResenaDeProductoForm()
    user_has_reviewed = False
    is_artisan_owner = False
    siguiendo_tienda = False

    if request.user.is_authenticated:
        es_favorito = Favorito.objects.filter(usuario=request.user, producto=producto).exists()
        user_has_reviewed = ResenaDeProducto.objects.filter(producto=producto, autor=request.user).exists()
        siguiendo_tienda = SeguirTienda.objects.filter(usuario=request.user, tienda=producto.tienda).exists()
        if hasattr(request.user, 'perfil') and request.user.perfil.rol == 'artesano':
            is_artisan_owner = (producto.tienda.artesano.user == request.user)

    context = {
        'producto': producto,
        'resenas': resenas,
        'es_favorito': es_favorito,
        'resena_form': resena_form,
        'user_has_reviewed': user_has_reviewed,
        'is_artisan_owner': is_artisan_owner,
        'siguiendo_tienda': siguiendo_tienda,
    }
    return render(request, 'detalle_producto.html', context)

@login_required
def crear_resena(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if request.method == 'POST':
        if producto.tienda.artesano.user == request.user:
            messages.error(request, "No puedes reseñar tu propio producto.")
            return redirect('detalle_producto', producto_id=producto_id)

        if ResenaDeProducto.objects.filter(producto=producto, autor=request.user).exists():
            messages.error(request, "Ya has enviado una reseña para este producto.")
            return redirect('detalle_producto', producto_id=producto_id)

        form = ResenaDeProductoForm(request.POST)
        if form.is_valid():
            resena = form.save(commit=False)
            resena.producto = producto
            resena.autor = request.user
            resena.save()
            messages.success(request, "Tu reseña ha sido enviada con éxito.")
            return redirect('detalle_producto', producto_id=producto_id)
        else:
            resenas = producto.resenas.filter(activa=True).order_by('-fecha_creacion')
            es_favorito = False
            user_has_reviewed = False
            is_artisan_owner = False
            if request.user.is_authenticated:
                es_favorito = Favorito.objects.filter(usuario=request.user, producto=producto).exists()
                user_has_reviewed = ResenaDeProducto.objects.filter(producto=producto, autor=request.user).exists()
                if hasattr(request.user, 'perfil') and request.user.perfil.rol == 'artesano':
                    is_artisan_owner = (producto.tienda.artesano.user == request.user)

            context = {
                'producto': producto,
                'resenas': resenas,
                'es_favorito': es_favorito,
                'resena_form': form,
                'user_has_reviewed': user_has_reviewed,
                'is_artisan_owner': is_artisan_owner,
            }
            messages.error(request, "Hubo un error con tu reseña. Por favor, verifica los datos.")
            return render(request, 'detalle_producto.html', context)

    return redirect('detalle_producto', producto_id=producto_id)




def login_usuario(request):
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
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('login')

def registro_artesano(request):
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
        messages.success(request, "¡Registro de artesano exitoso! 🎉 Ahora puedes iniciar sesión.")
        return redirect('login')
    return render(request, 'registro_artesano.html')

def registro_comprador(request):
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
        messages.success(request, "¡Registro de comprador exitoso! 🎉 Ahora puedes iniciar sesión.")
        return redirect('login')
    return render(request, 'registro_comprador.html')



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
    productos_list = tienda.productos.filter(activo=True).order_by('nombre')
    paginator = Paginator(productos_list, 6)  # 6 productos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    pedidos = Pedido.objects.filter(producto__in=productos_list).order_by('-fecha_creacion')
    context = {'tienda': tienda, 'productos': page_obj, 'pedidos': pedidos}
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
            
            # Notificar a los seguidores
            seguidores = SeguirTienda.objects.filter(tienda=tienda)
            notificaciones = []
            for seguimiento in seguidores:
                notificaciones.append(Notificacion(
                    usuario=seguimiento.usuario,
                    mensaje=f"¡Nuevo en {tienda.nombre}! Han publicado: {producto.nombre}",
                    tipo='general',
                    url=reverse('detalle_producto', args=[producto.id])
                ))
            if notificaciones:
                Notificacion.objects.bulk_create(notificaciones)

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
    producto = get_object_or_404(Producto, id=producto_id, tienda__artesano__user=request.user)
    
    if request.method == 'POST':
        nombre_producto = producto.nombre

        if Pedido.objects.filter(producto=producto, estado='P').exists():
            messages.error(request, f"No se puede ocultar '{nombre_producto}' porque tiene pedidos pendientes.")
            return redirect('mi_tienda')

        producto.activo = False
        producto.save()
        
        messages.success(request, f"Producto '{nombre_producto}' ha sido ocultado de la tienda.")
        return redirect('mi_tienda')

    return render(request, 'confirmar_eliminar_producto.html', {'producto': producto})

@login_required
def actualizar_estado_pedido(request, pedido_id, nuevo_estado):
    if not hasattr(request.user, 'perfil') or request.user.perfil.rol != 'artesano':
        messages.error(request, "No tienes permiso para realizar esta acción.")
        return redirect('home')

    pedido = get_object_or_404(Pedido, id=pedido_id)

    if pedido.producto.tienda.artesano != request.user.perfil:
        messages.error(request, "No puedes modificar un pedido que no te pertenece.")
        return redirect('mi_tienda')

    estados_validos = [estado[0] for estado in Pedido.ESTADOS]
    if nuevo_estado not in estados_validos:
        messages.error(request, f"Estado '{nuevo_estado}' no es válido.")
        return redirect('mi_tienda')

    pedido.estado = nuevo_estado
    pedido.save()

    if nuevo_estado == 'R':
        producto = pedido.producto
        producto.stock += pedido.cantidad
        producto.save()
        mensaje_notificacion = f"Tu pedido de {pedido.producto.nombre} ha sido rechazado por el artesano."
    elif nuevo_estado == 'C':
        mensaje_notificacion = f"¡Tu pedido de {pedido.producto.nombre} ha sido completado!"
    else:
        mensaje_notificacion = f"El estado de tu pedido de {pedido.producto.nombre} ha cambiado a {pedido.get_estado_display()}."

    if pedido.comprador != pedido.producto.tienda.artesano.user:
        Notificacion.objects.create(
            usuario=pedido.comprador,
            mensaje=mensaje_notificacion,
            tipo='pedido'
        )

    messages.success(request, f"El pedido #{pedido.id} ha sido actualizado a '{pedido.get_estado_display()}'.")
    return redirect('mi_tienda')
    
@login_required
def simular_pedido(request, producto_id):
    """Crea un pedido verificando stock disponible."""
    producto = get_object_or_404(Producto, id=producto_id)
    if request.user.is_authenticated and hasattr(request.user, 'perfil') and request.user.perfil.rol == 'artesano':
        if producto.tienda.artesano.user == request.user:
            messages.error(request, "No puedes comprar tu propio producto.")
            return redirect('detalle_producto', producto_id=producto.id)

    if producto.stock < 1:
        messages.error(request, f"❌ Lo sentimos, {producto.nombre} está agotado.")
        return redirect('detalle_producto', producto_id=producto_id)
    Pedido.objects.create(producto=producto, comprador=request.user, cantidad=1)
    producto.stock -= 1
    producto.save()
    Notificacion.objects.create(
        usuario=producto.tienda.artesano.user,
        mensaje=f"Nuevo pedido de {producto.nombre} por {request.user.username}",
        tipo='pedido'
    )
    messages.success(request, f"✅ Pedido de {producto.nombre} realizado exitosamente.")
    return redirect('mis_pedidos')

@login_required
def mis_pedidos(request):
    pedidos = Pedido.objects.filter(comprador=request.user).select_related('producto__tienda').order_by('-fecha_creacion')
    return render(request, 'mis_pedidos.html', {'pedidos': pedidos})

@login_required
def cancelar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, comprador=request.user)
    
    if pedido.estado == 'P':
        producto = pedido.producto
        producto.stock += pedido.cantidad
        producto.save()
        
        pedido.estado = 'CA'
        pedido.save()
        
        Notificacion.objects.create(
            usuario=producto.tienda.artesano.user,
            mensaje=f"El pedido #{pedido.id} de {producto.nombre} fue cancelado por el comprador.",
            tipo='pedido'
        )
        
        messages.success(request, f"El pedido #{pedido.id} ha sido cancelado correctamente.")
    else:
        messages.error(request, "Este pedido no se puede cancelar porque ya ha sido procesado.")
        
    return redirect('mis_pedidos')



@login_required
def toggle_favorito(request, producto_id):
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
    favoritos = Favorito.objects.filter(usuario=request.user).select_related('producto__tienda')
    return render(request, 'mis_favoritos.html', {'favoritos': favoritos})



@login_required
@login_required
def mis_notificaciones(request):
    notificaciones = Notificacion.objects.filter(usuario=request.user).order_by('-fecha_creacion')
    
    # Filtrar notificaciones
    notificaciones_pedido = notificaciones.filter(tipo='pedido')
    notificaciones_otras = notificaciones.exclude(tipo='pedido')
    
    # Marcar como leídas
    notificaciones.filter(leida=False).update(leida=True)
    
    context = {
        'notificaciones': notificaciones,
        'notificaciones_pedido': notificaciones_pedido,
        'notificaciones_otras': notificaciones_otras,
    }
    return render(request, 'mis_notificaciones.html', context)



@login_required
@staff_member_required
def admin_dashboard(request):
    total_usuarios = User.objects.count()
    total_productos = Producto.objects.count()
    total_tiendas = Tienda.objects.count()
    
    # Pendientes de moderación/atención
    tiendas_pendientes = Tienda.objects.filter(aprobada=False)
    resenas_pendientes = ResenaDeProducto.objects.filter(aprobada=False, activa=True)
    tickets_pendientes = SoporteTicket.objects.filter(estado='abierto')
    reportes_pendientes = ReporteAbuso.objects.filter(estado='pendiente')

    ultimos_pedidos = Pedido.objects.order_by('-fecha_creacion')[:5]
    ultimos_usuarios = User.objects.order_by('-date_joined')[:5]
    
    context = {
        'total_usuarios': total_usuarios,
        'total_productos': total_productos,
        'total_tiendas': total_tiendas,
        'tiendas_pendientes_count': tiendas_pendientes.count(),
        'resenas_pendientes_count': resenas_pendientes.count(),
        'tickets_pendientes_count': tickets_pendientes.count(),
        'reportes_pendientes_count': reportes_pendientes.count(),
        'tiendas_pendientes': tiendas_pendientes, # List
        'resenas': resenas_pendientes,            # List (renamed to match template expectation if any, usually 'resenas_pendientes' is improved name but template had 'resenas')
        'tickets': tickets_pendientes,            # List
        'reportes': reportes_pendientes,          # List
        'ultimos_pedidos': ultimos_pedidos,
        'ultimos_usuarios': ultimos_usuarios,
    }
    return render(request, 'admin.html', context)


# --- VISTAS DEL MÓDULO ADMINISTRATIVO Y COMUNICACIÓN ---

@login_required
def soporte_view(request):
    """HU-14: Soporte Técnico"""
    tickets = SoporteTicket.objects.filter(usuario=request.user).order_by('-fecha_creacion')
    if request.method == 'POST':
        form = SoporteTicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.usuario = request.user
            ticket.save()
            messages.success(request, "Ticket de soporte creado. Te responderemos pronto.")
            return redirect('soporte')
    else:
        form = SoporteTicketForm()
    return render(request, 'soporte.html', {'form': form, 'tickets': tickets})

@login_required
def chat_inbox(request):
    """HU-18: Chat Interno (Bandeja)"""
    conversaciones = Conversacion.objects.filter(
        Q(participante_1=request.user) | Q(participante_2=request.user)
    ).order_by('-fecha_actualizacion')
    return render(request, 'chat_inbox.html', {'conversaciones': conversaciones})

@login_required
def chat_thread(request, usuario_id):
    """HU-18: Chat Interno (Hilo)"""
    otro_usuario = get_object_or_404(User, id=usuario_id)
    if request.user == otro_usuario:
        return redirect('home')

    # Buscar o crear conversación
    conversacion = Conversacion.objects.filter(
        (Q(participante_1=request.user) & Q(participante_2=otro_usuario)) |
        (Q(participante_1=otro_usuario) & Q(participante_2=request.user))
    ).first()

    if not conversacion:
        # Restriccion: Artesano no puede iniciar chat con Comprador
        if hasattr(request.user, 'perfil') and request.user.perfil.rol == 'artesano':
             if hasattr(otro_usuario, 'perfil') and otro_usuario.perfil.rol == 'comprador':
                 messages.error(request, "Los vendedores no pueden iniciar conversaciones con clientes. Debes esperar a que ellos te contacten.")
                 return redirect('home')

        conversacion = Conversacion.objects.create(participante_1=request.user, participante_2=otro_usuario)

    if request.method == 'POST':
        form = MensajeChatForm(request.POST)
        if form.is_valid():
            mensaje = form.save(commit=False)
            mensaje.conversacion = conversacion
            mensaje.remitente = request.user
            mensaje.save()
            conversacion.fecha_actualizacion = timezone.now()
            conversacion.save()
            return redirect('chat_thread', usuario_id=usuario_id)
    else:
        form = MensajeChatForm()

    mensajes = conversacion.mensajes.order_by('fecha_envio')
    # Marcar leídos
    mensajes.filter(leido=False).exclude(remitente=request.user).update(leido=True)

    return render(request, 'chat_thread.html', {
        'conversacion': conversacion,
        'mensajes': mensajes,
        'form': form,
        'otro_usuario': otro_usuario
    })

@login_required
def reportar_abuso(request, content_type_str, object_id):
    """HU-22: Reportar Producto o Tienda"""
    # content_type_str debe ser 'producto' o 'tienda'
    if content_type_str == 'producto':
        model = Producto
    elif content_type_str == 'tienda':
        model = Tienda
    else:
        return redirect('home')

    obj = get_object_or_404(model, id=object_id)
    content_type = ContentType.objects.get_for_model(model)

    if request.method == 'POST':
        form = ReporteAbusoForm(request.POST)
        if form.is_valid():
            reporte = form.save(commit=False)
            reporte.reportante = request.user
            reporte.content_type = content_type
            reporte.object_id = object_id
            reporte.save()
            messages.success(request, "Reporte enviado. Gracias por ayudarnos a mantener segura la comunidad.")
            # Redirigir a la misma página (detalle del objeto)
            if content_type_str == 'producto':
                return redirect('detalle_producto', producto_id=object_id)
            elif content_type_str == 'tienda':
                return redirect('catalogo')
            return redirect('home')
    else:
        form = ReporteAbusoForm()
    
    return render(request, 'reportar_abuso.html', {'form': form, 'obj': obj})

@login_required
def seguir_tienda(request, tienda_id):
    """HU-23: Seguir Tienda"""
    tienda = get_object_or_404(Tienda, id=tienda_id)
    seguimiento = SeguirTienda.objects.filter(usuario=request.user, tienda=tienda).first()
    
    if seguimiento:
        seguimiento.delete()
        messages.info(request, f"Dejaste de seguir a {tienda.nombre}.")
    else:
        SeguirTienda.objects.create(usuario=request.user, tienda=tienda)
        messages.success(request, f"Ahora sigues a {tienda.nombre} 🎉")
        
        # Notificar al artesano
        Notificacion.objects.create(
            usuario=tienda.artesano.user,
            mensaje=f"{request.user.username} comenzó a seguir tu tienda.",
            tipo='general'
        )
    
    # Redirigir a la página desde la que vino si es posible, o a mi_tienda como fallback
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('catalogo')