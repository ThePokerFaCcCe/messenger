# Generated by Django 3.2.10 on 2021-12-30 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='token',
            field=models.CharField(auto_created=True, db_index=True, editable=False, max_length=128, verbose_name='Token'),
        ),
    ]
