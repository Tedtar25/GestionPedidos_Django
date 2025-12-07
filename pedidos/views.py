from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Pedido, ItemPedido
from .forms import CrearPedidoForm
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect
from .models import Cliente, Pedido

# Create your views here.

def lista_pedidos(request):
    pedidos = Pedido.objects.select_related("cliente").all()

    contexto = {
        "pedidos": pedidos
    }

    return render(request, "pedidos/lista_pedidos.html", contexto)

def detalle_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    items = pedido.itempedido_set.all()  # relación inversa

    contexto = {
        "pedido": pedido,
        "items": items,
    }
    return render(request, "pedidos/detalle_pedido.html", contexto)

@login_required
def mis_pedidos(request):
    if request.user.is_staff:
        return redirect("lista_pedidos")

    cliente = get_object_or_404(Cliente, user=request.user)
    pedidos = Pedido.objects.filter(cliente=cliente).order_by("-fecha_pedido")

    return render(request, "pedidos/mis_pedidos.html", {"pedidos": pedidos})

@login_required
def mis_pedidos_detalle(request, pedido_id):
    cliente = request.user.cliente
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=cliente)
    items = pedido.itempedido_set.all()

    contexto = {
        "pedido": pedido,
        "items": items,
    }
    return render(request, "pedidos/mis_pedidos_detalle.html", contexto)

@login_required
def crear_pedido(request):
    cliente = request.user.cliente

    if request.method == "POST":
        form = CrearPedidoForm(request.POST)
        if form.is_valid():
            producto = form.cleaned_data["producto"]
            cantidad = form.cleaned_data["cantidad"]

            pedido = Pedido.objects.create(
                cliente=cliente,
                subtotal=0,
                impuestos=0,
                total=0,
                estado=Pedido.Estado.PENDIENTE,
            )

            ItemPedido.objects.create(
                pedido=pedido,
                producto=producto,
                nombre_producto="",
                precio_unitario=0,
                cantidad=cantidad,
                impuesto_unitario=0,
                subtotal=0,
                total=0,
            )

            return redirect("mis_pedidos_detalle", pedido_id=pedido.id)
    else:
        form = CrearPedidoForm()

    return render(request, "pedidos/crear_pedido.html", {"form": form})

@login_required
def cancelar_pedido(request, pedido_id):
    cliente = request.user.cliente
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=cliente)

    if pedido.estado == Pedido.Estado.PENDIENTE:
        pedido.estado = Pedido.Estado.CANCELADO
        pedido.save(update_fields=["estado"])

    return redirect("mis_pedidos_detalle", pedido_id=pedido.id)

@staff_member_required
def lista_pedidos(request):
    pedidos = Pedido.objects.all().order_by("-fecha_pedido")
    return render(request, "pedidos/lista_pedidos.html", {"pedidos": pedidos})
