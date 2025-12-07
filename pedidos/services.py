from decimal import Decimal
from .models import Pedido


def calcular_total_ventas(pedidos):
    return sum((pedido.total for pedido in pedidos), Decimal("0"))


def contar_pedidos_por_estado(pedidos, estado_codigo):
    return sum(1 for pedido in pedidos if pedido.estado == estado_codigo)
