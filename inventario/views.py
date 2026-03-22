from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProductoForm
from .models import Producto

# --- MESERO PARA AGREGAR NUEVOS PRODUCTOS ---
@login_required(login_url='login')
def agregar_producto(request):
    
    # 🔒 SEGURIDAD EXTREMA: Si no es el Jefe, lo pateamos fuera de aquí
    if not request.user.is_superuser:
        return redirect('ver_inventario')

    # Si el Jefe presionó el botón de "Guardar" (POST)
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save() # Guardamos el producto en la base de datos
            return redirect('ver_inventario') # Lo regresamos a su tabla para que vea su nuevo producto
            
    # Si el Jefe recién entra a la página a ver la hoja en blanco (GET)
    else:
        form = ProductoForm()

    # Le mostramos la pantalla con la hoja lista para llenar
    return render(request, 'inventario/agregar_producto.html', {'form': form})

@login_required
def sumar_stock(request, producto_id):
    # 🛑 Seguridad: Solo el Jefe puede sumar mercadería nueva
    if not request.user.is_superuser or request.method != 'POST':
        return redirect('ver_inventario')

    # Buscamos el producto exacto al que le diste clic
    producto = get_object_or_404(Producto, id=producto_id)
    
    # Atrapamos el número que escribiste en la cajita de la tabla
    cantidad_nueva = int(request.POST.get('cantidad', 0))

    if cantidad_nueva > 0:
        # Sumamos la mercancía nueva al stock que ya tenías
        producto.stock_actual += cantidad_nueva
        producto.save()
        messages.success(request, f'✅ ¡Se agregaron {cantidad_nueva} unidades a {producto.nombre}!')
    
    # Te regresamos a la misma tabla para que sigas trabajando
    return redirect('ver_inventario')
