# Generated by Django 4.2.11 on 2024-07-09 02:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cliente', '0003_alter_cliente_ruc'),
        ('proveedor', '0003_proveedor_pais'),
        ('factura', '0008_alter_factura_fecha_vencimiento'),
    ]

    operations = [
        migrations.AddField(
            model_name='factura',
            name='proveedor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='proveedor.proveedor'),
        ),
        migrations.AlterField(
            model_name='factura',
            name='cliente',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='cliente.cliente'),
        ),
    ]
