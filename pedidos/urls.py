from django.urls import path
from . import views

urlpatterns = [
    path("pedidos/", views.lista_pedidos, name="lista_pedidos"),
    path("pedidos/<int:pedido_id>/", views.detalle_pedido, name="detalle_pedido"),
    path("mis-pedidos/", views.mis_pedidos, name="mis_pedidos"),
    path("mis-pedidos/nuevo/", views.crear_pedido, name="crear_pedido"),
    path("mis-pedidos/<int:pedido_id>/", views.mis_pedidos_detalle, name="mis_pedidos_detalle"),
    path("mis-pedidos/<int:pedido_id>/cancelar/", views.cancelar_pedido, name="cancelar_pedido"),
]