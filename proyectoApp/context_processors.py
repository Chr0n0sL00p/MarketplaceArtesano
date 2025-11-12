from .models import Perfil, Tienda

def tienda_context(request):
    if request.user.is_authenticated:
        try:
            perfil = Perfil.objects.get(user=request.user)
            tienda = Tienda.objects.filter(artesano=perfil).first()
            return {'tiene_tienda': bool(tienda)}
        except Perfil.DoesNotExist:
            return {'tiene_tienda': False}
    return {'tiene_tienda': False}
