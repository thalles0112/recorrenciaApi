# Generated by Django 4.1.4 on 2023-07-07 13:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_remove_recorrencia_produtos_delete_produto'),
    ]

    operations = [
        migrations.CreateModel(
            name='Produto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sku_nome', models.CharField(max_length=128)),
                ('sku_ref', models.CharField(max_length=16, unique=True)),
                ('sku_url', models.CharField(max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='recorrencia',
            name='produtos',
            field=models.ManyToManyField(blank=True, default='', to='api.produto'),
        ),
    ]
