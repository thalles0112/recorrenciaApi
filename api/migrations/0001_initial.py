# Generated by Django 4.1.4 on 2022-12-16 13:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Recorrencia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cliente_CPF_CNPJ', models.BigIntegerField()),
                ('data', models.DateField()),
                ('n_pedido', models.CharField(max_length=32)),
                ('nome_razao_social', models.CharField(max_length=128)),
                ('pedido_pgmto', models.CharField(max_length=64)),
                ('pedido_valor', models.FloatField()),
            ],
        ),
    ]
