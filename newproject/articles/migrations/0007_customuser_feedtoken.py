# Generated by Django 5.0.8 on 2024-08-12 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0006_orderrecord_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='feedToken',
            field=models.CharField(default=123456987, max_length=255),
            preserve_default=False,
        ),
    ]
