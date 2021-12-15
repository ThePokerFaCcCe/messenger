from cryptography.fernet import InvalidToken
from django.contrib.auth.models import PermissionsMixin
from django.conf import settings
from django.core.mail import send_mail
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db.models import F
from django.db.models.deletion import CASCADE
from django.db.models.fields.related import ForeignKey
from django.db.models.base import Model
from django.db.models.expressions import ExpressionWrapper
from django.db.models.fields import BooleanField, CharField, DateTimeField, EmailField, IntegerField, PositiveSmallIntegerField
from django.db.models.manager import Manager
from django.db import models
from django.db.models.query import QuerySet
from django.db.models.query_utils import Q
from django.db.utils import ProgrammingError
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from encrypt_decrypt_fields import EncryptedBinaryField, Crypto
from datetime import timedelta
from random import randint

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
    offline_after = timedelta(seconds=20)
    """After this time from user's `last_seen`, user's `is_online` will return `False`"""

    objects = UserManager()

    first_name = CharField(_('first name'), max_length=40)
    last_name = CharField(_('last name'), max_length=40, null=True)
    bio = CharField(_('Biography'), max_length=90, null=True)
    username = CharField(
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
    REQUIRED_FIELDS = ['first_name']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    @property
    def full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'.strip()

    @property
    def is_online(self) -> bool:
        """Returns `False` if `20` seconds passed from `last_seen`"""
        return ((timezone.now() - self.last_seen) < self.offline_after)

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
        if not (self.first_name and self.is_active):
            self.first_name = "temp user"
        return super().save(*args, **kwargs)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class VerifyCodeManager(Manager):

    def annotate_expires_at(self) -> QuerySet:
        """Return QuerySet object that contains `expires_at` field
        for filtering"""
        # https://stackoverflow.com/a/35658634/14034832
        return self.get_queryset().annotate(
            expires_at=ExpressionWrapper(
                F('created_at') + self.model.expire_after,
                output_field=DateTimeField()
            )
        )

    def filter_unexpired(self) -> QuerySet:
        """Return QuerySet object that contains only unexpired codes"""
        return self.annotate_expires_at().filter(
            expires_at__gt=timezone.now(),
            _tries__lt=self.model.max_tries
        )

    def filter_expired(self) -> QuerySet:
        """Return QuerySet object that contains only expired codes"""
        return self.annotate_expires_at().filter(
            Q(expires_at__lte=timezone.now()) |
            Q(_tries__gte=self.model.max_tries)
        )

    def delete_expired(self) -> None:
        """Delete expired codes"""
        self.filter_expired().delete()


class VerifyCode(Model):
    def generate_code(*args, **kwargs) -> str:
        """Returns 6-digit unique code"""
        max_digit = 6
        numbers = []

        i = 0
        while i < max_digit:
            num = randint(0, 9)
            if i != 0:
                prev_num = numbers[i-1]
                if any([
                    str(num) == prev_num,
                    num+1 == prev_num,
                    num-1 == prev_num,
                ]):
                    continue
            numbers.append(str(num))
            i += 1

        return ''.join(numbers)

    expire_after = timedelta(minutes=1)
    max_tries = 3

    _expires_at = None
    _dec_code = None

    objects = VerifyCodeManager()

    _code = EncryptedBinaryField(verbose_name=_("Code"), auto_created=True,
                                 key=settings.VERIFYCODE_KEY, editable=False,
                                 default=generate_code, db_index=True)

    _tries = PositiveSmallIntegerField(default=0)
    created_at = DateTimeField(_("Created at"), auto_now_add=True, editable=False)

    user = ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=CASCADE)

    @property
    def code(self) -> str:
        if self._dec_code is None:
            try:
                self._dec_code = Crypto(settings.VERIFYCODE_KEY).decrypt_token(
                    self._code if isinstance(self._code, bytes)
                    else bytes(self._code, 'utf-8')
                )
            except InvalidToken:
                self._dec_code = self._code
        return self._dec_code

    @property
    def expires_at(self) -> timezone:
        if self._expires_at is None:
            self._expires_at = self.created_at + self.expire_after
        return self._expires_at

    @expires_at.setter
    def expires_at(self, value: timezone):
        self._expires_at = value

    @property
    def is_expired(self) -> bool:
        """Returns `True` if `expire_date` passed or `max_tries` exceeded"""
        return (
            ((timezone.now() - self.created_at) > self.expire_after)
            or self._tries >= self.max_tries
        )

    @property
    def tries(self) -> int:
        return self._tries

    def increase_tries(self, save: bool = False, **save_kwargs) -> int:
        """Increase `tries` by 1 and return new `tries`

        Parameters
        ----------
        `save : bool` Save new tries to database

        `**save_kwargs` Kwargs that need to pass when calling `.save()`
        """
        self._tries += 1
        if save:
            self.save(**save_kwargs)

        return self.tries

    def check_code(self, code) -> bool:
        """Checks if entered code is same as encrypted code"""
        return code == self.code
