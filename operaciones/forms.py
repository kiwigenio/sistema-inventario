from django import forms
from .models import Cliente,Campana

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        # Aquí le decimos a Django: "SOLO muéstrale al trabajador estos campos"
        # ¡Todo lo demás (restante, procesado, vendedor, pedido) quedará invisible para ellos!
        fields = [
            'tipo_envio', 
            'nombre', 
            'dni', 
            'telefono', 
            'departamento', 
            'agencia_destino', 
            'monto_inicial', 
            'monto_final',
            'producto_asignado', 
            'regalo',
            'clave',
            'comentario',
            'estado_envio',
        ]
        
        # Le ponemos un poco de diseño básico a las cajitas para que se vean bien
        widgets = {
            'tipo_envio': forms.Select(attrs={'class': 'form-control'}),
            'departamento': forms.Select(attrs={'class': 'form-control'}),
            'comentario': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
   
    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop('usuario', None)  # Extraemos el usuario de los argumentos
        super(ClienteForm, self).__init__(*args, **kwargs)

        # Esto hace que todas las cajitas de texto tengan el mismo diseño bonito (form-control)
        if usuario : 
            if usuario.is_superuser:
                pass
            else :
                try:
                    campana_del_trabajador = Campana.objects.get(trabajador_asignado=usuario)
                    self.fields['producto_asignado'].queryset = campana_del_trabajador.productos.all()
                except Campana.DoesNotExist:
                    self.fields['producto_asignado'].queryset = self.fields['producto_asignado'].queryset.none()

class EdicionClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'tipo_envio', 
            'nombre', 
            'dni', 
            'telefono', 
            'departamento', 
            'agencia_destino', 
            'monto_inicial', 
            'monto_final',
            'producto_asignado', 
            'regalo',
            'clave',
            'comentario',
            'estado_envio',
        ]
        
        widgets = {
            'tipo_envio': forms.Select(attrs={'class': 'form-control'}),
            'departamento': forms.Select(attrs={'class': 'form-control'}),
            'comentario': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }