from django.db import models
from uuid import uuid1


def create_negative_uuid():
    return -int(uuid1().int >> 72)


class NegativeUUIDMixin:
    id = models.BigIntegerField(primary_key=True, db_index=True,
                                auto_created=True, unique=True)

    def save(self, *args, **kwargs):
        if self.id is None:
            uuid = create_negative_uuid()

            while self.__class__.objects.filter(
                    id=uuid).exists():
                uuid = create_negative_uuid()

            self.id = uuid

        return super().save(*args, **kwargs)
