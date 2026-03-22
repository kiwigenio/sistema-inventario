from django.core.management.base import BaseCommand
from operaciones.models import Cliente
from inventario.models import Producto
from django.db import transaction

class Command(BaseCommand):
    help = 'Resta el stock de productos basados en las ventas no procesadas'

    def handle(self, *args, **options):
        # 1. Buscamos todos los clientes que NO han sido procesados
        clientes_pendientes = Cliente.objects.filter(procesado_inventario=False)
        
        if not clientes_pendientes.exists():
            self.stdout.write("No hay ventas nuevas para procesar.")
            return

        # Usamos una transacción para que, si algo falla, no se reste nada a medias
        with transaction.atomic():
            for cliente in clientes_pendientes:
                producto = cliente.producto_asignado
                
                # 2. Restamos 1 al stock (puedes ajustar si un cliente lleva más)
                if producto.stock_actual > 0:
                    producto.stock_actual -= 1
                    producto.save()
                    
                    # 3. Marcamos al cliente como procesado (El interruptor a "SÍ")
                    cliente.procesado_inventario = True
                    cliente.save()
                    
                    self.stdout.write(f"Procesado: {cliente.nombre} - Producto: {producto.nombre}")
                else:
                    self.stdout.write(self.style.WARNING(f"¡ALERTA! Sin stock para {producto.nombre}"))

        self.stdout.write(self.style.SUCCESS('Sincronización de inventario terminada con éxito.'))