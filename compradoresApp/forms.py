# compradoresApp/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Review

class CompradorLoginForm(AuthenticationForm):
    username = forms.CharField(label="Usuario", widget=forms.TextInput(attrs={'placeholder': 'usuario'}))
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'placeholder': 'contraseña'}))

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'rows': 4}),
        }

class FilterForm(forms.Form):
    category = forms.CharField(required=False)
    location = forms.CharField(required=False)
    min_price = forms.DecimalField(required=False, decimal_places=2, max_digits=10)
    max_price = forms.DecimalField(required=False, decimal_places=2, max_digits=10)
