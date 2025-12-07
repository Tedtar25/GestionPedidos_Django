from django.test import TestCase
from decimal import Decimal
from django.contrib.auth.models import User
from .models import Cliente, Producto, Pedido, ItemPedido
from .services import calcular_total_ventas, contar_pedidos_por_estado

# Create your tests here.
class ServiciosPedidosTests(TestCase):
    def setUp(self):
        # Usuario con cliente
        self.user = User.objects.create_user(username="cliente1", password="test1234")
        self.cliente = Cliente.objects.create(
            user=self.user,
            nombre="Cliente Prueba",
            email="cliente@example.com",
            telefono="4771234567",
            calle="Calle 1",
            num_exterior="100",
            num_interior="",
            colonia="Centro",
            ciudad="León",
            estado="Guanajuato",
            codigo_postal="37000",
        )

        # Producto
        self.producto = Producto.objects.create(
            nombre="Laptop Prueba",
            precio_unitario=Decimal("10000.00"),
            impuesto_unitario=Decimal("1600.00"),
        )

        # Pedido con un item
        self.pedido1 = Pedido.objects.create(
            cliente=self.cliente,
            subtotal=Decimal("0"),
            impuestos=Decimal("0"),
            total=Decimal("0"),
            estado=Pedido.Estado.PENDIENTE,
        )
        ItemPedido.objects.create(
            pedido=self.pedido1,
            producto=self.producto,
            nombre_producto=self.producto.nombre,
            precio_unitario=self.producto.precio_unitario,
            cantidad=1,
            impuesto_unitario=self.producto.impuesto_unitario,
            subtotal=self.producto.precio_unitario,
            total=self.producto.precio_unitario + self.producto.impuesto_unitario,
        )
        # Calcular totales del pedido
        self.pedido1.actualizar_totales()

        # Pedido en otro estado
        self.pedido2 = Pedido.objects.create(
            cliente=self.cliente,
            subtotal=Decimal("0"),
            impuestos=Decimal("0"),
            total=Decimal("0"),
            estado=Pedido.Estado.ENTREGADO,
        )

    def test_calcular_total_ventas(self):
        pedidos = [self.pedido1, self.pedido2]

        total_ventas = calcular_total_ventas(pedidos)

        # 3 asserts mínimos
        self.assertIsInstance(total_ventas, Decimal)
        self.assertGreater(total_ventas, Decimal("0"))
        self.assertEqual(total_ventas, self.pedido1.total + self.pedido2.total)

    def test_contar_pedidos_por_estado(self):
        pedidos = [self.pedido1, self.pedido2]

        pendientes = contar_pedidos_por_estado(pedidos, Pedido.Estado.PENDIENTE)
        entregados = contar_pedidos_por_estado(pedidos, Pedido.Estado.ENTREGADO)
        cancelados = contar_pedidos_por_estado(pedidos, Pedido.Estado.CANCELADO)

        # 3 asserts mínimos
        self.assertEqual(pendientes, 1)
        self.assertEqual(entregados, 1)
        self.assertEqual(cancelados, 0)

class ModeloPedidoItemTests(TestCase):
    def setUp(self):
        # Usuario + cliente
        self.user = User.objects.create_user(username="cliente2", password="test1234")
        self.cliente = Cliente.objects.create(
            user=self.user,
            nombre="Cliente Modelo",
            email="modelocliente@example.com",
            telefono="4777654321",
            calle="Calle 2",
            num_exterior="200",
            num_interior="",
            colonia="Centro",
            ciudad="León",
            estado="Guanajuato",
            codigo_postal="37000",
        )

        # Producto base
        self.producto = Producto.objects.create(
            nombre="Monitor Prueba",
            precio_unitario=Decimal("5000.00"),
            impuesto_unitario=Decimal("800.00"),
        )

        # Pedido vacío inicialmente
        self.pedido = Pedido.objects.create(
            cliente=self.cliente,
            subtotal=Decimal("0"),
            impuestos=Decimal("0"),
            total=Decimal("0"),
            estado=Pedido.Estado.PENDIENTE,
        )

    def test_itempedido_save_copia_datos_y_calcula_importes(self):
        item = ItemPedido.objects.create(
            pedido=self.pedido,
            producto=self.producto,
            nombre_producto="",          # se debe rellenar en save()
            precio_unitario=Decimal("0"),  # se sobrescribe en save()
            cantidad=2,
            impuesto_unitario=Decimal("0"),  # se sobrescribe en save()
            subtotal=Decimal("0"),         # se calcula en save()
            total=Decimal("0"),            # se calcula en save()
        )

        # 3 asserts (mínimo)
        self.assertEqual(item.nombre_producto, self.producto.nombre)
        self.assertEqual(item.precio_unitario, self.producto.precio_unitario)
        self.assertEqual(
            item.subtotal,
            self.producto.precio_unitario * item.cantidad
        )

        # Extras para estar seguros
        self.assertEqual(item.impuesto_unitario, self.producto.impuesto_unitario)
        self.assertEqual(
            item.total,
            (self.producto.precio_unitario + self.producto.impuesto_unitario) * item.cantidad
        )

    def test_pedido_actualizar_totales_suma_items_correctamente(self):
        # Creamos dos items para el mismo pedido
        item1 = ItemPedido.objects.create(
            pedido=self.pedido,
            producto=self.producto,
            nombre_producto=self.producto.nombre,
            precio_unitario=self.producto.precio_unitario,
            cantidad=1,
            impuesto_unitario=self.producto.impuesto_unitario,
            subtotal=self.producto.precio_unitario,
            total=self.producto.precio_unitario + self.producto.impuesto_unitario,
        )

        item2 = ItemPedido.objects.create(
            pedido=self.pedido,
            producto=self.producto,
            nombre_producto=self.producto.nombre,
            precio_unitario=self.producto.precio_unitario,
            cantidad=3,
            impuesto_unitario=self.producto.impuesto_unitario,
            subtotal=self.producto.precio_unitario * 3,
            total=(self.producto.precio_unitario + self.producto.impuesto_unitario) * 3,
        )

        # Forzamos recálculo por si acaso
        self.pedido.actualizar_totales()
        self.pedido.refresh_from_db()

        subtotal_esperado = item1.subtotal + item2.subtotal
        impuestos_esperados = (
            item1.impuesto_unitario * item1.cantidad +
            item2.impuesto_unitario * item2.cantidad
        )
        total_esperado = subtotal_esperado + impuestos_esperados

        # 3 asserts mínimos
        self.assertEqual(self.pedido.subtotal, subtotal_esperado)
        self.assertEqual(self.pedido.impuestos, impuestos_esperados)
        self.assertEqual(self.pedido.total, total_esperado)