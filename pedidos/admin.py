from django.contrib import admin
from .models import Cliente, Producto, Pedido, ItemPedido

# Register your models here.
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "email", "telefono", "ciudad", "estado")
    search_fields = ("nombre", "email", "telefono")


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "precio_unitario", "impuesto_unitario", "activo")
    list_filter = ("activo",)



class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 1
    readonly_fields = ("nombre_producto", "precio_unitario", "impuesto_unitario", "subtotal", "total")


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ("id", "cliente", "fecha_pedido", "estado", "paqueteria", "fecha_entrega", "total")
    list_filter = ("estado", "paqueteria", "fecha_pedido")
    search_fields = ("cliente__nombre", "cliente__email")
    inlines = [ItemPedidoInline]
    readonly_fields = ("subtotal", "impuestos", "total")
