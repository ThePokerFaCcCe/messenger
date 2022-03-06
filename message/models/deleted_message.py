from django.db import models
from django.conf import settings

from .message import Message


class DeletedMessage(models.Model):
    message = models.ForeignKey(to=Message, on_delete=models.CASCADE,
                                related_name='deleted_for_users')
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='deleted_messages')
    deleted_at = models.DateTimeField(auto_now_add=True)
