"""
URL configuration for inventario_web project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from operaciones.views import registrar_venta,lista_clientes,editar_cliente,lista_campanas,clientes_por_campana,ver_inventario, salir,enviar_reporte_excel  
from django.contrib.auth import views as auth_views
from inventario.views import agregar_producto, sumar_stock


urlpatterns = [
    #panel de admin
    path('admin/logout/',salir),
    path('admin/', admin.site.urls),

    #login y logout
    path('',auth_views.LoginView.as_view(template_name='operaciones/login.html',redirect_authenticated_user= True), name='login'),
    #path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    path('campana', lista_campanas, name='lista_campanas'),
    path('campana/<int:campana_id>/clientes/', clientes_por_campana, name='clientes_por_campana'),

    #proceso de registrar un cliente
    path('ventas',registrar_venta, name='registrar_venta'),
    path('clientes',lista_clientes, name='lista_clientes'),
    path('clientes/editar/<int:id>/', editar_cliente, name='editar_cliente'), 

    #inventario 
    path('inventario/',ver_inventario, name='ver_inventario'),

    path('logout/', salir, name='logout'),

    # Ruta secreta del Jefe para agregar mercadería
    path('inventario/agregar/', agregar_producto, name='agregar_producto'),

    # Ruta para el botón del Excel
    path('clientes/exportar-excel/', enviar_reporte_excel, name='enviar_reporte_excel'),

    # Ruta para que el botón de sumar stock funcione
    path('inventario/sumar-stock/<int:producto_id>/', sumar_stock, name='sumar_stock'),





]
