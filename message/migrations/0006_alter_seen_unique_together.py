# Generated by Django 3.2.12 on 2022-03-13 14:33

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('message', '0005_alter_seen_options'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='seen',
            unique_together={('user', 'message')},
        ),
    ]
