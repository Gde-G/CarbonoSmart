# Generated by Django 4.2.2 on 2023-09-06 20:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='keywords',
            field=models.CharField(default='Huella de carbono, Carbono en argentina, Oportunidad em argentina', max_length=100),
            preserve_default=False,
        ),
    ]
