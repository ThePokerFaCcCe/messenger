

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('message', '0004_seen'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='seen',
            options={'ordering': ['-seen_at']},
        ),
    ]
