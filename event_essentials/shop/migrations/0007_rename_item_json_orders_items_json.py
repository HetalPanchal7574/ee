# Generated by Django 5.0.1 on 2024-04-07 09:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0006_alter_orders_address_alter_orders_city_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orders',
            old_name='item_json',
            new_name='items_json',
        ),
    ]