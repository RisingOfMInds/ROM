# Generated by Django 2.1.2 on 2019-04-05 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_auto_20190203_0855'),
    ]

    operations = [
        migrations.AddField(
            model_name='blog',
            name='active',
            field=models.BooleanField(default=False),
        ),
    ]
