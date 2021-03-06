# Generated by Django 3.2.10 on 2022-01-03 15:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_access'),
    ]

    operations = [
        migrations.AddField(
            model_name='verifycode',
            name='is_used',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AlterField(
            model_name='verifycode',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='verify_codes', to=settings.AUTH_USER_MODEL),
        ),
    ]
