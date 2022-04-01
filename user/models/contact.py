from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

User = settings.AUTH_USER_MODEL


class Contact(models.Model):
    first_name = models.CharField(_('first name'), max_length=40)
    last_name = models.CharField(_('last name'), max_length=40, null=True)

    contacted_user = models.ForeignKey(User, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='contacts')

    @property
    def full_name(self) -> str:
        return f'{self.first_name} {self.last_name or ""}'.strip()

    class Meta:
        unique_together = ['contacted_user', 'user']
