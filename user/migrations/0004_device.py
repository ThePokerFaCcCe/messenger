# Generated by Django 3.2.10 on 2021-12-18 18:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import picturic.fields
import picturic.utils


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_encrypt_code_user_fk'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profile_image',
            field=picturic.fields.PictureField(max_length=9999, null=True, upload_to=picturic.utils.upload_to_path, verbose_name='Profile image'),
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(auto_created=True, db_index=True, editable=False, max_length=128, verbose_name='Device token')),
                ('type', models.CharField(choices=[('windows', 'Windows'), ('android', 'Android'), ('ios', 'IOS'), ('other', 'Other')], max_length=15, verbose_name='Device type')),
                ('model', models.CharField(max_length=50, verbose_name='Device model')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
