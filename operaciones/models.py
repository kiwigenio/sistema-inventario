
from django.db import models
from django.contrib.auth.models import User
from inventario.models import Producto
from django.utils import timezone


# Create your models here.
# la campañande ventas por cada temporada
class Campana(models.Model):
    nombre = models.CharField(max_length=100)
    trabajador_asignado = models.ForeignKey(User, on_delete=models.CASCADE) 
    fecha_inicio = models.DateField(auto_now_add=True)
    activa = models.BooleanField(default=True)
    productos = models.ManyToManyField(Producto)

    def __str__(self):
        return self.nombre
    
# la clase de cliente para registrar los usuarios 
class Cliente(models.Model):   
    TIPO_ENVIOS_OPCIONES = [
        ('SHALOM','shalom' ),
        ('DELIVERY', 'delivery'),
        ('OTRA_AGENCIA', 'otra_agencia'),
    ]

    DEPARTAMENTOS_OPCIONES = [
        ('AMAZONAS', 'Amazonas'), ('ANCASH', 'Áncash'), ('APURIMAC', 'Apurímac'),
        ('AREQUIPA', 'Arequipa'), ('AYACUCHO', 'Ayacucho'), ('CAJAMARCA', 'Cajamarca'),
        ('CALLAO', 'Callao'), ('CUSCO', 'Cusco'), ('HUANCAVELICA', 'Huancavelica'),
        ('HUANUCO', 'Huánuco'), ('ICA', 'Ica'), ('JUNIN', 'Junín'),
        ('LA_LIBERTAD', 'La Libertad'), ('LAMBAYEQUE', 'Lambayeque'), ('LIMA', 'Lima'),
        ('LORETO', 'Loreto'), ('MADRE_DE_DIOS', 'Madre de Dios'), ('MOQUEGUA', 'Moquegua'),
        ('PASCO', 'Pasco'), ('PIURA', 'Piura'), ('PUNO', 'Puno'),
        ('SAN_MARTIN', 'San Martín'), ('TACNA', 'Tacna'), ('TUMBES', 'Tumbes'),
        ('UCAYALI', 'Ucayali'),
    ]

    ESTADO_PEDIDO_OPCIONES = [ 
        ('POR_ENVIAR', 'Por enviar'),
        ('EN_TRANSITO', 'En transito'),
        ('LLEGO_FALTA_PAGAR', 'Llego pero falta pagar'),
        ('CANCELADO', 'Cancelado'),
        ('RETORNO', 'Retorno'),
    ]

    tipo_envio = models.CharField(max_length=20, choices=TIPO_ENVIOS_OPCIONES, default='SHALOM')
    nombre = models.CharField(max_length = 100, blank = True, null = True)
    dni = models.CharField(max_length = 20, blank = True, null = True)

    telefono = models.CharField(max_length = 20)
    departamento = models.CharField(max_length=20, choices= DEPARTAMENTOS_OPCIONES, default='LIMA')
    agencia_destino = models.CharField(max_length=100)

    fecha_registro = models.DateField(default = timezone.now)
    numero_pedido = models.PositiveIntegerField(editable = False)

    monto_inicial = models.IntegerField( default= 0, blank = True, null= True)
    monto_final = models.IntegerField( default= 0, blank = True, null =True)

    restante = models.IntegerField(default= 0)

    clave = models.CharField(max_length = 4)
    comentario = models.TextField(blank =True, null= True)

    campana = models.ForeignKey('Campana', on_delete = models.CASCADE)
    producto_asignado = models.ForeignKey(Producto, on_delete = models.PROTECT)
    procesado_inventario = models.BooleanField(default=False)

    estado_envio = models.CharField(max_length=20, choices=ESTADO_PEDIDO_OPCIONES, default='POR_ENVIAR')

    regalo = models.BooleanField(default=False)


    def save(self, *arg,**kwargs):
        if self.tipo_envio == 'DELIVERY':
            self.departamento = 'LIMA'
            self.nombre = self.nombre or 'CLIENTE DELIVERY'
        else : 
            if self.monto_final and self.monto_inicial:
                self.restante = self.monto_final - self.monto_inicial
        if not self.id:
            hoy = timezone.now().date()
            ventas_hoy = Cliente.objects.filter(fecha_registro=hoy).count()
            self.numero_pedido = ventas_hoy + 1

        if self.estado_envio != 'RETORNO' and self.procesado_inventario == False and self.producto_asignado:
            self.producto_asignado.stock_actual -= 1 
            self.producto_asignado.save()
            self.procesado_inventario = True # Lo marcamos como descontado
            
        # CASO B: Devolución por cancelación (Sumamos stock)
        # Si el estado es CANCELADO y SÍ había sido procesado (descontado) antes:
        elif self.estado_envio == 'RETORNO' and self.procesado_inventario == True and self.producto_asignado:
            self.producto_asignado.stock_actual += 1 # Le devolvemos 1 al almacén
            self.producto_asignado.save()
            self.procesado_inventario = False

        super(Cliente,self).save(*arg,**kwargs)

# --- MESERO PARA EXPORTAR EXCEL Y ENVIAR POR CORREO ---
