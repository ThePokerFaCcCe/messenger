from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

User = settings.AUTH_USER_MODEL


class PrivateChat(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    creator = models.ForeignKey(
        to=User, on_delete=models.SET_NULL, null=True, blank=True,
        help_text=_("The user that started conversation"))

    users = models.ManyToManyField(to=User,
                                   related_name="private_chats")

    def get_reciever_user(self, sender_user):
        """Returns reciever user"""
        users = self.users.all()
        if sender_user in users:
            user = list(filter(
                lambda item: item != sender_user, users
            ))
            return user[0] if user else sender_user
