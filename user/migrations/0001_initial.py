# Generated by Django 3.2.10 on 2021-12-11 12:12

import django.core.validators
from django.db import migrations, models
import picturic.fields
import picturic.utils
import user.models
import user.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(max_length=40, verbose_name='first name')),
                ('last_name', models.CharField(max_length=40, null=True, verbose_name='last name')),
                ('bio', models.CharField(max_length=90, null=True, verbose_name='Biography')),
                ('username', models.CharField(db_index=True, error_messages={'unique': 'A user with that username already exists.'}, help_text='Username must start with English letters and contain numbers and one underscore ( _ ). 4-60chars only ', max_length=60, null=True, unique=True, validators=[user.validators.UsernameValidator(), django.core.validators.MinLengthValidator(4, 'Username must have at least 4 chars'), django.core.validators.MaxLengthValidator(60, 'Username can have at last 60 chars')], verbose_name='username')),
                ('profile_image', picturic.fields.PictureField(max_length=9999, null=True, upload_to=picturic.utils.upload_to_path, verbose_name='Profile image')),
                ('last_seen', models.DateTimeField(auto_now_add=True, help_text='Last time user was online', verbose_name='Last seen')),
                ('email', models.EmailField(db_index=True, max_length=254, unique=True, verbose_name='email')),
                ('is_staff', models.BooleanField(default=False, help_text='Is user staff or not', verbose_name='is staff')),
                ('is_bot', models.BooleanField(default=False, help_text='Is user bot or not', verbose_name='is bot')),
                ('is_active', models.BooleanField(default=False, help_text='Is user active or not', verbose_name='is active')),
                ('is_scam', models.BooleanField(default=False, help_text='Is user scam or not', verbose_name='is scam')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            bases=(user.models.AutoFieldStartCountMixin, models.Model),
        ),
    ]