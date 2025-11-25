# core/forms.py
from django import forms
from .models import Tienda, Producto, Categoria, ResenaDeProducto
from django.utils.text import slugify

class ResenaDeProductoForm(forms.ModelForm):
    calificacion = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Calificación'
    )

    class Meta:
        model = ResenaDeProducto
        fields = ['calificacion', 'comentario']
        widgets = {
            'comentario': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Escribe tu reseña aquí...'}),
        }
        labels = {
            'comentario': 'Comentario',
        }


class TiendaForm(forms.ModelForm):
    """
    Formulario para la creación y edición de una Tienda.
    """
    class Meta:
        model = Tienda
        fields = ['nombre', 'descripcion', 'ubicacion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de tu tienda'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe tu tienda, tu historia, tus productos...'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ciudad, Región'}),
        }
        labels = {
            'nombre': 'Nombre de la Tienda',
            'descripcion': 'Descripción',
            'ubicacion': 'Ubicación',
        }

class ProductoForm(forms.ModelForm):
    """
    Formulario para la creación y edición de un Producto, con la capacidad
    de crear una nueva categoría dinámicamente.
    """
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Categoría existente"
    )
    nueva_categoria = forms.CharField(
        max_length=100,
        required=False,
        label="O crea una nueva categoría",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Cerámica, Tejidos, etc.'})
    )

    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'stock', 'imagen', 'categoria', 'nueva_categoria']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'precio': 'Precio en CLP.',
            'imagen': 'Sube una imagen representativa de tu producto.',
        }

    def clean(self):
        cleaned_data = super().clean()
        categoria = cleaned_data.get("categoria")
        nueva_categoria = cleaned_data.get("nueva_categoria")

        if not categoria and not nueva_categoria:
            raise forms.ValidationError("Debes seleccionar una categoría existente o crear una nueva.", code='no_category')
        
        if categoria and nueva_categoria:
            raise forms.ValidationError("Por favor, selecciona una categoría o crea una nueva, pero no ambas.", code='category_conflict')

        return cleaned_data

    def save(self, commit=True):
        # Primero, gestionamos la categoría
        nueva_categoria_nombre = self.cleaned_data.get('nueva_categoria', '').strip()
        
        if nueva_categoria_nombre:
            # Si el usuario escribió una nueva categoría, la creamos o la obtenemos si ya existe
            categoria, _ = Categoria.objects.get_or_create(
                nombre=nueva_categoria_nombre,
                defaults={'slug': slugify(nueva_categoria_nombre)}
            )
            # Asignamos esta categoría a la instancia del producto
            self.instance.categoria = categoria
        
        # Eliminamos 'nueva_categoria' de los datos del formulario ya que no es un campo del modelo Producto
        if 'nueva_categoria' in self.cleaned_data:
            del self.cleaned_data['nueva_categoria']

        return super().save(commit)
