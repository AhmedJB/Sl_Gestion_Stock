# Generated by Django 4.1.1 on 2023-07-05 20:19

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('controller', '0021_account_example_prismamigrations_session_testtest_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Testtest',
        ),
        migrations.AlterField(
            model_name='echeance',
            name='dateEcheance',
            field=models.DateTimeField(default=datetime.datetime(2023, 7, 5, 20, 19, 3, 491902, tzinfo=datetime.timezone.utc)),
        ),
    ]
