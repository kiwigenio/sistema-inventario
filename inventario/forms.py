from django import forms
from .models import Producto 

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        # Aquí ponemos los nombres EXACTOS de tu base de datos
        fields = ['nombre', 'descripcion', 'stock_actual'] 
        # Le ponemos el diseño "form-control" para que se vea profesional
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Teclado Gamer'}),
            # Usamos Textarea para la descripción porque puede ser un texto largo
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Ej. Color negro, luces RGB...', 'rows': 3}),
            'stock_actual': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 100'}),
        }