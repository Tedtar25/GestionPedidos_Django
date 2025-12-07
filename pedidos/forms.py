from django import forms
from .models import Producto

class CrearPedidoForm(forms.Form):
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.all(),
        label="Producto"
    )
    cantidad = forms.IntegerField(
        min_value=1,
        initial=1,
        label="Cantidad"
    )
