# Generated by Django 3.2.10 on 2022-01-03 21:13

from django.db import migrations, models
import picturic.fields
import picturic.utils


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_alter_verify_add_is_used'),
    ]

    operations = [
        migrations.AlterField(
            model_name='access',
            name='token',
            field=models.CharField(auto_created=True, db_index=True, max_length=128, null=True, verbose_name='Token'),
        ),
        migrations.AlterField(
            model_name='device',
            name='token',
            field=models.CharField(auto_created=True, db_index=True, max_length=128, null=True, verbose_name='Token'),
        ),
    ]
