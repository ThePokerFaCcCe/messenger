# Generated by Django 3.2.11 on 2022-02-05 16:28

from django.db import migrations, models
import picturic.fields
import picturic.utils


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0009_remove_user_username'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='is_bot',
        ),
        migrations.AddField(
            model_name='user',
            name='type',
            field=models.CharField(choices=[('U', 'User'), ('B', 'Bot')], default='U', max_length=1, verbose_name='User type'),
        ),
    ]
