# Generated by Django 4.1.1 on 2023-07-07 22:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('controller', '0004_delete_testdjangomodel'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Account',
        ),
        migrations.DeleteModel(
            name='Example',
        ),
        migrations.DeleteModel(
            name='PrismaMigrations',
        ),
        migrations.DeleteModel(
            name='Session',
        ),
        migrations.DeleteModel(
            name='Testtest',
        ),
        migrations.DeleteModel(
            name='User',
        ),
        migrations.DeleteModel(
            name='Userinformation',
        ),
        migrations.DeleteModel(
            name='Verificationtoken',
        ),
    ]
