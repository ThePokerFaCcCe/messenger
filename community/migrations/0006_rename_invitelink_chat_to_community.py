# Generated by Django 3.2.11 on 2022-02-11 21:05

from django.db import migrations
import picturic.fields
import picturic.utils


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0005_use_soft_delete_mixin'),
    ]

    operations = [
        migrations.RenameField(
            model_name='invitelink',
            old_name='chat',
            new_name='community',
        ),
    ]
