# Generated by Django 3.2.10 on 2022-01-03 21:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_alter_token_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='verifycode',
            name='token',
            field=models.CharField(auto_created=True, db_index=True, max_length=128, null=True, verbose_name='Token'),
        ),
    ]