# Generated by Django 5.0.4 on 2024-04-08 01:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('factura', '0003_factura_sub_total_iva_factura_sub_total_iva_10_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='itemfactura',
            name='total',
        ),
    ]
