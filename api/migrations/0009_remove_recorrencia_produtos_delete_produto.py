# Generated by Django 4.1.4 on 2023-07-07 13:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_excelfile_file_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recorrencia',
            name='produtos',
        ),
        migrations.DeleteModel(
            name='Produto',
        ),
    ]