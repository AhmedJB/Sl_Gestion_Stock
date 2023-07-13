# Generated by Django 4.1.1 on 2023-06-28 15:00

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('controller', '0018_alter_client_id_alter_customuser_id_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='OptionCategories',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('value', models.CharField(max_length=255)),
            ],
        ),
        migrations.AlterField(
            model_name='echeance',
            name='dateEcheance',
            field=models.DateTimeField(default=datetime.datetime(2023, 6, 28, 15, 0, 13, 617040, tzinfo=datetime.timezone.utc)),
        ),
    ]