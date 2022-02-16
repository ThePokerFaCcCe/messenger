from django.db.models.manager import BaseManager
from ..queryset import SoftDeleteQuerySet


class SoftDeleteManager(BaseManager.from_queryset(
        SoftDeleteQuerySet)):
    pass
