from django.db.models import CharField
# from django_fake_model import models as f

from global_id.models.mixins import GUIDMixin


class FakeChat(GUIDMixin):
    name = CharField(max_length=255, blank=True,
                     null=True)
