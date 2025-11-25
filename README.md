# Marketplace Artesanal - Proyecto Integrado

## 📋 Descripción

Marketplace Artesanal es una plataforma e-commerce desarrollada en Django que conecta artesanos locales con compradores. Los artesanos pueden crear tiendas virtuales, gestionar productos y recibir pedidos, mientras que los compradores pueden explorar el catálogo, agregar productos a favoritos y realizar pedidos.

## 🚀 Tecnologías Utilizadas

- **Backend**: Django 4.2.26 (Python)
- **Base de Datos**: MySQL (usando PyMySQL 1.1.2)
- **Manejo de Imágenes**: Pillow 12.0.0
- **Configuración**: python-decouple 3.8
- **Frontend**: HTML, CSS vanilla
- **Idioma**: Español (Chile) - `es-cl`

## 📦 Instalación

### Prerrequisitos

- Python 3.8 o superior
- MySQL Server
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <url-del-repositorio>
   cd proyecto-Integrado
   ```

2. **Crear y activar entorno virtual**
   ```bash
   python -m venv venv
   # En Windows:
   venv\Scripts\activate
   # En Linux/Mac:
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**
   
   Copia el archivo `.env.example` a `.env` y configura tus variables:
   ```bash
   copy .env.example .env  # En Windows
   cp .env.example .env    # En Linux/Mac
   ```
   
   Edita el archivo `.env` con tus configuraciones:
   ```env
   SECRET_KEY=tu-secret-key-generada
   DEBUG=True
   DB_NAME=proyectoIntegradoDB
   DB_USER=root
   DB_PASSWORD=tu-password-mysql
   DB_HOST=localhost
   DB_PORT=3306
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

   **Generar SECRET_KEY:**
   ```python
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

5. **Crear la base de datos**
   
   Accede a MySQL y crea la base de datos:
   ```sql
   CREATE DATABASE proyectoIntegradoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

6. **Ejecutar migraciones**
   ```bash
   python manage.py migrate
   ```

7. **Crear superusuario (opcional)**
   ```bash
   python manage.py createsuperuser
   ```

8. **Ejecutar el servidor de desarrollo**
   ```bash
   python manage.py runserver
   ```

9. **Acceder a la aplicación**
   
   Abre tu navegador en: `http://localhost:8000`

## 🎯 Funcionalidades Principales

### Para Artesanos
- ✅ Registro y autenticación
- ✅ Creación de tienda virtual
- ✅ Gestión de productos (crear, editar, eliminar)
- ✅ Visualización de pedidos recibidos
- ✅ Sistema de notificaciones

### Para Compradores
- ✅ Registro y autenticación
- ✅ Exploración de catálogo con filtros y búsqueda
- ✅ Vista detallada de productos
- ✅ Sistema de favoritos
- ✅ Realización de pedidos
- ✅ Historial de pedidos
- ✅ Sistema de notificaciones

### Funcionalidades Generales
- ✅ Búsqueda de productos por nombre/descripción
- ✅ Filtrado por categorías
- ✅ Ordenamiento (precio, fecha, nombre)
- ✅ Paginación del catálogo
- ✅ Verificación de stock
- ✅ Sistema de reseñas de productos
- ✅ Panel de administración

## 📁 Estructura del Proyecto

```
proyecto-Integrado/
├── config/                 # Configuración del proyecto Django
│   ├── settings.py        # Configuraciones principales
│   ├── urls.py            # URLs principales
│   └── wsgi.py            # Configuración WSGI
├── core/                  # Aplicación principal
│   ├── migrations/        # Migraciones de base de datos
│   ├── admin.py           # Configuración del admin de Django
│   ├── models.py          # Modelos de datos
│   ├── views.py           # Vistas/controladores
│   ├── urls.py            # URLs de la app
│   ├── forms.py           # Formularios
│   └── context_processors.py  # Procesadores de contexto
├── templates/             # Plantillas HTML
├── static/                # Archivos estáticos (CSS, JS, imágenes)
├── media/                 # Archivos subidos por usuarios
├── manage.py              # Script de gestión de Django
├── requirements.txt       # Dependencias del proyecto
├── .env.example           # Ejemplo de variables de entorno
└── .gitignore             # Archivos ignorados por Git
```

## 🔒 Seguridad

### Configuraciones Implementadas

- ✅ SECRET_KEY protegida con variables de entorno
- ✅ Credenciales de base de datos en variables de entorno
- ✅ Validación de contraseñas con validadores de Django
- ✅ Protección CSRF habilitada
- ✅ Confirmación para acciones destructivas
- ✅ Verificación de permisos en vistas sensibles

### Recomendaciones para Producción

1. Cambiar `DEBUG = False`
2. Configurar `ALLOWED_HOSTS` correctamente
3. Usar HTTPS
4. Configurar archivos estáticos con servidor web (Nginx/Apache)
5. Usar una contraseña fuerte para la base de datos
6. Implementar rate limiting
7. Configurar backups automáticos

## 🧪 Testing

Para ejecutar las pruebas:
```bash
python manage.py test
```

## 📝 Uso

### Registro de Artesano
1. Ir a `/registro/artesano/`
2. Completar el formulario
3. Iniciar sesión
4. Crear una tienda
5. Agregar productos

### Registro de Comprador
1. Ir a `/registro/comprador/`
2. Completar el formulario
3. Iniciar sesión
4. Explorar el catálogo
5. Agregar productos a favoritos
6. Realizar pedidos

## 🐛 Problemas Conocidos

- Las migraciones pueden tener referencias incorrectas a 'proyectoApp' en lugar de 'core'
- El sistema de reseñas está implementado en el modelo pero falta la interfaz completa
- El carrito de compras no está implementado (solo pedidos individuales)

## 🔄 Próximas Mejoras

- [ ] Implementar carrito de compras completo
- [ ] Sistema completo de reseñas con interfaz
- [ ] Pasarela de pago real
- [ ] Sistema de mensajería entre usuarios
- [ ] Dashboard mejorado con gráficos
- [ ] Exportación de reportes
- [ ] API REST
- [ ] Tests automatizados completos

## 👥 Contribuir

1. Fork el proyecto
2. Crea una rama para tu funcionalidad (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## 📧 Contacto

Para preguntas o sugerencias, por favor abre un issue en el repositorio.

---

**Nota**: Este es un proyecto educativo. Para uso en producción, se recomienda realizar auditorías de seguridad adicionales y optimizaciones de rendimiento.
