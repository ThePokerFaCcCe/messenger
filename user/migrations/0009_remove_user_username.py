# Generated by Django 3.2.11 on 2022-02-04 20:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_delete_access_verifycode'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='username',
        ),
    ]
