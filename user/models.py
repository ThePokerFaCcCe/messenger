from django.contrib.auth.models import PermissionsMixin
from django.conf import settings
from django.core.mail import send_mail
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models
from django.db.models.base import Model
from django.db.models.fields import BooleanField, DateTimeField, EmailField
from django.db.models.manager import Manager
from django.db import models
from django.db.utils import ProgrammingError
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
from django.utils import timezone

from picturic.fields import PictureField
from .validators import UsernameValidator


class AutoFieldStartCountMixin:
    """Must be used when table is empty"""

    start_count_value = 1

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        try:
            if not self.__class__.objects.count():
                # I found some bugs here.
                # if we just clear the table from DB,
                # this code runs again!
                # And then if we create new objects,
                # their ID will start from start_count_value
                self.update_auto_increment()
        except ProgrammingError:
            pass

    def update_auto_increment(self):
        """Update auto increment start count"""
        # https://stackoverflow.com/a/15317333/14034832
        from django.db import connection, transaction, router

        cursor = connection.cursor()
        with transaction.atomic():
            _router = settings.DATABASES[router.db_for_write(self.__class__)]['NAME']
            alter_str = "ALTER table {}.{} AUTO_INCREMENT={}".format(
                _router, self._meta.db_table, self.start_count_value)
            cursor.execute(alter_str)


class UserManager(Manager):
    def _create_user(self, email, **extra_fields):
        """
        Create and save a user.
        """
        if not email:
            raise ValueError('The given email must be set')

        user = self.model(email=email, **extra_fields)
        user.save(using=self._db)
        return user

    def create_user(self, email, **extra_fields):
        return self._create_user(email, **extra_fields)

    def create_superuser(self, email, **extra_fields):
        return self._create_user(email, is_staff=True, is_superuser=True, **extra_fields)

    @classmethod
    def generate_random_token(cls):
        """
        Generate a random Token
        """
        length = 22
        allowed_chars = ('abcdefghjkmnpqrstuvwxyz'
                         'ABCDEFGHJKLMNPQRSTUVWXYZ'
                         '23456789&*()_-!$%=^')
        return get_random_string(length, allowed_chars)


class User(AutoFieldStartCountMixin, PermissionsMixin, Model):
    start_count_value = 10000000  # for AutoFieldStartCountMixin
    offline_after_sec = timedelta(seconds=20)
    """After this time from user's `last_seen`, user's `is_online` will return `False`"""

    objects = UserManager()

    first_name = models.CharField(_('first name'), max_length=40)
    last_name = models.CharField(_('last name'), max_length=40, null=True)
    bio = models.CharField(_('Biography'), max_length=90, null=True)
    username = models.CharField(
        _('username'),
        unique=True, null=True, max_length=60, db_index=True,
        help_text=_(('Username must start with English letters '
                     'and contain numbers and one underscore ( _ ). '
                     '4-60chars only ')),
        validators=[
            UsernameValidator(),
            MinLengthValidator(4, _("Username must have at least 4 chars")),
            MaxLengthValidator(60, _("Username can have at last 60 chars")),
        ],
        error_messages={
            'unique': _("A user with that username already exists."),
        },)
    profile_image = PictureField(verbose_name=_("Profile image"),
                                 use_upload_to_func=True, null=True)
    last_seen = DateTimeField(_("Last seen"), auto_now_add=True,
                              help_text=_("Last time user was online"))
    email = EmailField(_("email"), unique=True, db_index=True)

    is_staff = BooleanField(_("is staff"),
                            help_text="Is user staff or not",
                            default=False)

    is_bot = BooleanField(_("is bot"),
                          help_text="Is user bot or not",
                          default=False)

    is_active = BooleanField(_("is active"),
                             help_text="Is user active or not",
                             default=False)

    is_scam = BooleanField(_("is scam"),
                           help_text="Is user scam or not",
                           default=False)

    created_at = DateTimeField(auto_now_add=True, editable=False)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    @property
    def full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'.strip()

    @property
    def is_online(self) -> bool:
        """Returns `False` if `20` seconds passed from `last_seen`"""
        return ((timezone.now() - self.last_seen) < self.offline_after_sec)

    @property
    def is_anonymous(self):
        """
        Always return False. This is a way of comparing User objects to
        anonymous users.
        """
        return False

    @property
    def is_authenticated(self):
        """
        Always return True. This is a way to tell if the user has been
        authenticated in templates.
        """
        return True

    def set_online(self, save: bool = True, **save_kwargs) -> None:
        """Set user's last seen to `timezone.now()`

        Parameters
        ----------
        `save : bool` Save new last_seen to database

        `**save_kwargs` Kwargs that need to pass when calling `.save()`
        """
        self.last_seen = timezone.now()
        if save:
            self.save(**save_kwargs)

    def clean(self):
        super().clean()
        self.email = self.email.lower()

    def save(self, *args, **kwargs) -> None:
        self.clean()
        return super().save(*args, **kwargs)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)
