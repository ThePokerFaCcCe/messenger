from typing import Optional
from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from picturic.fields import PictureField
from global_id.models.mixins import GUIDMixin
from user.signals import user_online


class UserManager(models.Manager):
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

    @classmethod
    def normalize_email(cls, email: str) -> str:
        return email.lower()


class User(PermissionsMixin, GUIDMixin, models.Model):
    offline_after = timezone.timedelta(seconds=60)
    """After this time from user's `last_seen`, user's `is_online` will return `False`"""

    used_access = None
    """Access object that user authenticated with. only available in request.user"""

    used_device = None
    """Device object that user's access contains. only available in request.user"""

    objects = UserManager()

    class TypeChoices(models.TextChoices):
        USER = 'U', _("User")
        BOT = 'B', _("Bot")

    type = models.CharField(_('User type'), max_length=1,
                            choices=TypeChoices.choices,
                            default=TypeChoices.USER)

    first_name = models.CharField(_('first name'), max_length=40)
    last_name = models.CharField(_('last name'), max_length=40, null=True)
    bio = models.CharField(_('Biography'), max_length=90, null=True)
    profile_image = PictureField(verbose_name=_("Profile image"),
                                 use_upload_to_func=True, null=True,
                                 make_thumbnail=True,
                                 thumbnail_size=(150, 150))
    last_seen = models.DateTimeField(_("Last seen"), auto_now_add=True,
                                     help_text=_("Last time user was online"))
    email = models.EmailField(_("email"), unique=True, db_index=True)

    is_staff = models.BooleanField(_("is staff"),
                                   help_text="Is user staff or not",
                                   default=False)

    is_active = models.BooleanField(_("is active"),
                                    help_text="Is user active or not",
                                    default=False)

    is_scam = models.BooleanField(_("is scam"),
                                  help_text="Is user scam or not",
                                  default=False)

    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    @property
    def full_name(self) -> str:
        return f'{self.first_name} {self.last_name or ""}'.strip()

    @property
    def is_online(self) -> bool:
        """Returns `False` if now is passed from `offline_after`"""
        return ((timezone.now() - self.last_seen) < self.offline_after)

    @property
    def next_offline(self) -> Optional[timezone.datetime]:
        """Returns datetime that user will be offline after that
        or `None` if user is already offline"""
        if self.is_online:
            return (self.last_seen + self.offline_after).astimezone(
                timezone.get_current_timezone()
            )

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
        user_online.send(self.__class__, instance=self)
        if save:
            self.save(**save_kwargs)

    def delete_profile_image(self) -> None:
        """Delete user's `profile_image`"""

        if self.profile_image is not None:
            self.profile_image.delete()
            self.save()

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def save(self, *args, **kwargs) -> None:
        self.clean()
        if not (self.first_name and self.is_active):
            self.first_name = "temp user"
        return super().save(*args, **kwargs)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        email = getattr(self, self.EMAIL_FIELD)
        send_mail(subject, message, from_email, [email], **kwargs)
