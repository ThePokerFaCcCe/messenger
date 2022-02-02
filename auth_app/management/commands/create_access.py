from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.utils import generate_email
from auth_app.tests.utils import create_access

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates an active user and an access token for that'

    def add_arguments(self, parser) -> None:
        parser.add_argument('--admin', action="store_true",
                            help='make user admin')

    def handle(self, *args, **options):
        user = None
        if options['admin']:
            user = User.objects.create_superuser(
                email=generate_email(),
                is_active=True,
            )

        access = create_access(user, activate_user=True)
        self.stdout.write(
            self.style.SUCCESS(
                f"Access token:\n\nToken {access.encrypted_token}\n"
            )
        )
