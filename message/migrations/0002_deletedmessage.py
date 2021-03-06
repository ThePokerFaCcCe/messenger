# Generated by Django 3.2.12 on 2022-03-06 16:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('message', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeletedMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(auto_now_add=True)),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deleted_for_users', to='message.message')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deleted_messages', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
