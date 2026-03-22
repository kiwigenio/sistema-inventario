from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ClienteForm, EdicionClienteForm
from django.views.decorators.cache import never_cache
from django.contrib.auth import logout
from .models import Campana,Cliente
from inventario.models import Producto
from django.contrib import messages

import openpyxl
from io import BytesIO  
from django.core.mail import EmailMessage



@login_required
def registrar_venta(request):

    try : 
        campana_del_trabajador = Campana.objects.get(trabajador_asignado = request.user)
    except Campana.DoesNotExist: 
        campana_del_trabajador = None

    if request.method == 'POST':
        form = ClienteForm(request.POST, usuario=request.user)  # PASAMOS EL USUARIO ACTUAL AL FORMULARIO
        if form.is_valid():
            # 1. TRUCO MAGICO: commit=False
            # Le decimos: "Prepara los datos del cliente, pero TODAVÍA NO los guardes"
            nuevo_cliente = form.save(commit=False)
            if campana_del_trabajador : 
                nuevo_cliente.campana = campana_del_trabajador
            nuevo_cliente.save()

            if campana_del_trabajador : 
                return redirect('clientes_por_campana',campana_id = campana_del_trabajador.id)
            else : 
                return redirect('lista_campanas')

    else:
        form = ClienteForm(usuario=request.user)  # PASAMOS EL USUARIO ACTUAL AL FORMULARIO

    return render(request, 'operaciones/registrar_venta.html', {'form': form, 'campana': campana_del_trabajador})

@login_required
def lista_clientes(request):
    
    query = request.GET.get('q',"")

    if query: 
        clientes = Cliente.objects.filter(telefono__icontains=query).order_by('-id')
    
    else: 
        clientes = Cliente.objects.all().order_by('-id')
    return render(request, 'operaciones/lista_clientes.html', {'clientes': clientes, 'query':query})


@login_required
def editar_cliente(request, id):
    # Busca al cliente por su ID. Si no existe, da error 404
    cliente = get_object_or_404(Cliente, id=id)
    if request.user != cliente.campana.trabajador_asignado and not request.user.is_superuser:
        # Recoge los datos editados, PERO referenciando al cliente existente (instance=cliente)
        return redirect('lista_campanas')
    
    if request.method == 'POST':
        form = EdicionClienteForm(request.POST, instance = cliente)
        if form.is_valid():
            form.save()
            return redirect('clientes_por_campana', campana_id = cliente.campana.id)
    else:
        # Si apenas entra a la página, le muestra el formulario YA LLENO con los datos del cliente
        form = EdicionClienteForm(instance=cliente)
        
    return render(request, 'operaciones/editar_cliente.html', {'form': form, 'cliente': cliente})

@never_cache
@login_required
def lista_campanas(request):
    campanas  = Campana.objects.all()
    return render(request, 'operaciones/lista_campanas.html', {'campanas': campanas})


@login_required
def clientes_por_campana(request, campana_id): 
    campana = get_object_or_404(Campana, id=campana_id)
    # Atrapamos lo que el usuario escribió en la barra
    query = request.GET.get('q', "")
    if query:
        # Filtramos SOLO los clientes de ESTA campaña que coincidan con el teléfono
        clientes = Cliente.objects.filter(campana=campana, telefono__icontains=query).order_by('-id')
    else:
        # Si no buscó nada, mostramos todos los de la campaña
        clientes = Cliente.objects.filter(campana=campana).order_by('-id')
    return render(request, 'operaciones/lista_clientes.html', {'clientes': clientes, 'campana_actual': campana, 'query': query})


@login_required
def ver_inventario(request): 
    productos = Producto.objects.all()
    return render(request, 'operaciones/ver_inventario.html', {'productos': productos})

def salir(request):
    logout(request)
    return redirect('login')


def enviar_reporte_excel(request):
    
    if not request.user.is_superuser or request.method != 'POST':
        # TRUCO: HTTP_REFERER te regresa exactamente a la pantalla donde estabas
        return redirect(request.META.get('HTTP_REFERER', 'lista_clientes')) 

    correo_destino = request.POST.get('correo_escrito')

    try:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Reporte"

        titulos = ['Fecha', 'N° Pedido', 'Cliente', 'Teléfono', 'Producto', 'Tipo Envío', 'Destino', 'Estado', 'Costo', 'Restante', 'Clave', 'Comentario']
        ws.append(titulos)

        clientes = Cliente.objects.all().order_by('-fecha_registro')

        for c in clientes:
            ws.append([
                c.fecha_registro.strftime('%d-%m-%Y') if c.fecha_registro else '', 
                c.numero_pedido, c.nombre, c.telefono,
                c.producto_asignado.nombre if c.producto_asignado else 'Sin producto',
                c.tipo_envio, c.agencia_destino, c.estado_envio,
                c.monto_final, c.restante, c.clave, c.comentario
            ])

        archivo_memoria = BytesIO() 
        wb.save(archivo_memoria) 
        archivo_memoria.seek(0) 

        mensaje = EmailMessage(
            subject='📊 Tu Reporte de Ventas en Excel',
            body='Hola Jefe. El sistema ha generado su reporte de ventas automático.',
            from_email='empresa.comercio.e@gmail.com', 
            to=[correo_destino], 
        )
        
        mensaje.attach('Reportes_Clientes.xlsx', archivo_memoria.getvalue(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        mensaje.send()

        # 🎉 NOTIFICACIÓN DE ÉXITO
        messages.success(request, f'¡El Excel se envió correctamente a {correo_destino}!')

    except Exception as e:
        # 🚨 NOTIFICACIÓN DE ERROR (Si algo falla, te dirá exactamente qué fue)
        messages.error(request, f'Error al enviar el correo: {str(e)}')

    # Regresamos EXACTAMENTE a la tabla de la campaña donde le diste clic
    return redirect(request.META.get('HTTP_REFERER', 'lista_clientes'))