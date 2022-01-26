# Generated by Django 3.2.11 on 2022-01-26 21:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conversation', '0002_privatechat_creator'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversation',
            name='alias',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='Alias'),
        ),
        migrations.AddField(
            model_name='conversation',
            name='is_archived',
            field=models.BooleanField(default=False, verbose_name='Archived'),
        ),
        migrations.AddField(
            model_name='conversation',
            name='is_pinned',
            field=models.BooleanField(default=False, verbose_name='Pinned'),
        ),
    ]
