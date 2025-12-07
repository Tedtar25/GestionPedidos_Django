from django.db import models
from django.contrib.auth.models import User

# Create your models here.
############################################################
class Cliente(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="cliente"
    )

    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=10)
    calle = models.CharField(max_length=200)
    num_exterior = models.CharField(max_length=10)
    num_interior = models.CharField(max_length=10, blank=True, null=True)
    colonia = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=10)

    def __str__(self):
        return self.nombre

############################################################
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    impuesto_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True)  # <- NUEVO

    def __str__(self):
        return self.nombre

############################################################
class Pedido(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha_pedido = models.DateTimeField(auto_now_add=True)

    subtotal = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=0, blank=True, null=True
    )
    impuestos = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=0, blank=True, null=True
    )
    total = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=0, blank=True, null=True
    )

    class Estado(models.TextChoices):
        PENDIENTE = 'PE', 'Pendiente'
        PROCESANDO = 'PR', 'Procesando'
        ENVIADO = 'EN', 'Enviado'
        ENTREGADO = 'ET', 'Entregado'
        CANCELADO = 'CA', 'Cancelado'

    class Paqueteria(models.TextChoices):
        FEDEX = 'FEDEX', 'FedEx'
        DHL = 'DHL', 'DHL'

    estado = models.CharField(
        max_length=2,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )

    paqueteria = models.CharField(
        max_length=10,
        choices=Paqueteria.choices,
        blank=True,
        null=True,
    )
    fecha_entrega = models.DateField(
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"Pedido {self.id} - {self.cliente.nombre}"

    def actualizar_totales(self):
        items = self.itempedido_set.all()
        subtotal = sum(item.subtotal for item in items)
        impuestos = sum(item.impuesto_unitario * item.cantidad for item in items)
        total = subtotal + impuestos

        self.subtotal = subtotal
        self.impuestos = impuestos
        self.total = total
        self.save(update_fields=["subtotal", "impuestos", "total"])
############################################################
class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    nombre_producto = models.CharField(max_length=100)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.PositiveIntegerField()
    impuesto_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad} x {self.nombre_producto} for Pedido {self.pedido.id}"

    def save(self, *args, **kwargs):
        # Copiamos los datos del producto
        if self.producto:
            self.nombre_producto = self.producto.nombre
            self.precio_unitario = self.producto.precio_unitario
            self.impuesto_unitario = self.producto.impuesto_unitario

        # Calculamos importes
        self.subtotal = self.precio_unitario * self.cantidad
        self.total = (self.precio_unitario + self.impuesto_unitario) * self.cantidad

        super().save(*args, **kwargs)

        # Calcurla totales del pedido
        self.pedido.actualizar_totales()
