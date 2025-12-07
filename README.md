# Gestión de Pedidos – Django + MySQL

Proyecto escolar de gestión de pedidos desarrollado con **Django** y **MySQL**.
El sistema modela el último módulo de una tienda en línea: la parte de **gestión de pedidos** ya generados.

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

----------Crear la base de datos (desde MySQL Workbench o consola MySQL):----------

CREATE DATABASE gestion_pedidos;
USE gestion_pedidos;

DROP DATABASE IF EXISTS gestion_pedidos;

select * from pedidos_cliente;
select * from pedidos_itempedido;
select * from pedidos_pedido;
select * from pedidos_producto;

----------Editar gestion_pedidos/settings.py y configurar la sección DATABASES----------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'gestion_pedidos',
        'USER': 'root',              # o el usuario MySQL que uses
        'PASSWORD': 'tu_password',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

------------------------------------------------------------------------------------------
pip install mysqlclient
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
