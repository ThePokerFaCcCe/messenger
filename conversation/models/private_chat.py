from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class PrivateChat(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

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
