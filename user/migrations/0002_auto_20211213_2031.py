# Generated by Django 3.2.10 on 2021-12-13 17:01

from django.db import migrations, models
import picturic.fields
import picturic.utils
import user.models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='VerifyCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(auto_created=True, db_index=True, default=user.models.VerifyCode.generate_code, editable=False, max_length=6, verbose_name='Code')),
                ('email', models.EmailField(db_index=True, editable=False, max_length=254, verbose_name='Email')),
                ('_tries', models.PositiveSmallIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
            ],
        ),
    ]