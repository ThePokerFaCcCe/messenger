from typing import Any, Optional
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
from django.db.models.fields import BooleanField, CharField, DateTimeField, EmailField, PositiveSmallIntegerField
from django.db.models.manager import Manager
from django.db.models.enums import TextChoices
from django.db.models.query import QuerySet
from django.db.models.query_utils import Q
from django.db.utils import ProgrammingError
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth.hashers import BasePasswordHasher, PBKDF2PasswordHasher, SHA1PasswordHasher, make_password, check_password, MD5PasswordHasher
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
    max_digit = 6

    def generate_code(*args, **kwargs) -> str:
        """Returns 6-digit unique code"""
        numbers = []

        i = 0
        while i < VerifyCode.max_digit:
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
    _dec_code = 0

    objects = VerifyCodeManager()

    _code = EncryptedBinaryField(verbose_name=_("Code"), auto_created=True,
                                 key=settings.VERIFYCODE_KEY, editable=False,
                                 default=generate_code, db_index=True)

    _tries = PositiveSmallIntegerField(default=0)
    created_at = DateTimeField(_("Created at"), auto_now_add=True, editable=False)

    user = ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=CASCADE)

    @property
    def code(self) -> Optional[str]:
        """Return decrypted code if key was correct, else None"""
        if self._dec_code == 0:
            try:
                self._dec_code = Crypto(settings.VERIFYCODE_KEY).decrypt_token(
                    self._code if isinstance(self._code, bytes)
                    else bytes(self._code, 'utf-8')
                )
            except InvalidToken:
                self._dec_code = self._code if len(self._code) == self.max_digit else None
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


def hash_token(token, hasher=None):
    """Return hashed token"""
    return make_password(token, hasher=hasher)


def encrypt_token_and_value(encrypt_key, value, token) -> bytes:
    """Return encrypted string with this format: '`value`@`token`'"""
    return Crypto(encrypt_key).encrypt(f"{value}@{token}")


def decrypt_token_and_value(encrypt_key, encrypted_text: str
                            ) -> Optional[tuple[str, str]]:
    """Return a tuple that contains (value, token) if 
    `encrypted_text` is valid else return `None`"""

    try:
        decrypted_value = Crypto(encrypt_key).decrypt_token(
            bytes(encrypted_text, encoding='utf-8')
        )
    except InvalidToken:
        return None

    splitted_value = decrypted_value.split("@", 1)
    if len(splitted_value) == 2 and all(splitted_value):
        return splitted_value


def generate_token(instance=None, length=24, key=None, hasher: BasePasswordHasher = None):
    """Return auto-generated hashed token and set `_unhashed_token` 
    to unhashed token in instance if `instance` is passed.

    Parameters
    ----------
    `length` will read from `_token_length` attr if exists in `instance`(default is 24).

    `hasher` will read from `_hasher` attr if exists in `instance`(default is None)."""

    if instance:
        length = getattr(instance, '_token_length', length)
        hasher = getattr(instance, '_hasher', hasher)

    token = get_random_string(length=length)
    hashed_token = hash_token(token, hasher)

    if instance:
        setattr(instance, "_unhashed_token", token)
    return hashed_token


class EncryptedTokenManager(Manager):
    def find_token(self, encrypted_token) -> Optional[Any]:
        key = getattr(self.model, '_encrypt_key', None)
        assert key is not None, "You must set `_encrypt_key` attr in your model"

        if value := decrypt_token_and_value(key, encrypted_token):
            instance_id, token = value

            if instance := self.filter(pk=instance_id):
                instance = instance[0]

                if self.check_token(token, instance.token):
                    return instance

    @classmethod
    def check_token(cls, token: str, hashed_token: str) -> bool:
        """Return `True` if raw `token` is same as `hashed_token`"""
        return check_password(token, hashed_token)


class Device(Model):
    _token_length = 32
    _hasher: BasePasswordHasher = PBKDF2PasswordHasher()
    _encrypt_key = settings.DEVICETOKEN_KEY
    _unhashed_token = None

    objects = EncryptedTokenManager()

    class TypeChoices(TextChoices):
        WINDOWS = 'windows', 'Windows'
        ANDROID = 'android', 'Android'
        IOS = 'ios', 'IOS'
        OTHER = 'other', 'Other'

    type = CharField(_("Device type"), max_length=15, choices=TypeChoices.choices)
    model = CharField(_("Device model"), max_length=50)

    token = CharField(db_index=True, max_length=128, editable=False,
                      verbose_name=_("Device token"), auto_created=True)
    created_at = DateTimeField(auto_now_add=True)

    user = ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=CASCADE)

    @property
    def unhashed_token(self) -> Optional[str]:
        """Only return generated unhashed token 
        when model is just created. otherwise return `None`"""
        return self._unhashed_token

    def save(self, *args, **kwargs):
        editing = bool(self.token)
        if not editing:
            self.token = generate_token(instance=self)
        super().save(*args, **kwargs)
        if not editing:
            self.__encrypt_unhashed_token()

    def __encrypt_unhashed_token(self):
        """Encrypts `_unhashed_token` and `pk` together and set it
         to `_unhashed_token`. You need to set `_encrypt_key` attr """

        self._unhashed_token = encrypt_token_and_value(
            self._encrypt_key,
            self.pk,
            self._unhashed_token
        ).decode("utf-8")
