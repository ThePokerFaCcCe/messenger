

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('message', '0002_deletedmessage'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='message',
            options={'ordering': ['-id']},
        ),
    ]
