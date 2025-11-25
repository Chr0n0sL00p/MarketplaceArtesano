from .models import Perfil, Tienda, Notificacion

def tienda_context(request):
    context = {'tiene_tienda': False, 'notificaciones_count': 0}
    
    if request.user.is_authenticated:
        try:
            perfil = Perfil.objects.get(user=request.user)
            tienda = Tienda.objects.filter(artesano=perfil).first()
            context['tiene_tienda'] = bool(tienda)
            
            # Contar notificaciones no leídas
            notificaciones_count = Notificacion.objects.filter(
                usuario=request.user, 
                leida=False
            ).count()
            context['notificaciones_count'] = notificaciones_count
            
        except Perfil.DoesNotExist:
            pass
    
    return context
