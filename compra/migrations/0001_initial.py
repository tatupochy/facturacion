# Generated by Django 5.0.4 on 2024-07-13 19:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('factura', '0010_factura_operacion'),
        ('producto', '0004_producto_stock'),
        ('proveedor', '0003_proveedor_pais'),
    ]

    operations = [
        migrations.CreateModel(
            name='Compra',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.IntegerField()),
                ('factura', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='factura.factura')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='producto.producto')),
                ('proveedor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='proveedor.proveedor')),
            ],
        ),
    ]
