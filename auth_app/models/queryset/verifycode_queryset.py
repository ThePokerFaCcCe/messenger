from django.utils import timezone
from django.db.models import F
from django.db.models.expressions import ExpressionWrapper
from django.db.models.fields import DateTimeField
from django.db.models.query import QuerySet
from django.db.models.query_utils import Q


class VerifyCodeQuerySet(QuerySet):

    def annotate_expires_at(self) -> QuerySet:
        """Return QuerySet object that contains `expires_at` field
        for filtering"""
        # https://stackoverflow.com/a/35658634/14034832
        return self.annotate(
            expires_at=ExpressionWrapper(
                F('created_at') + self.model.expire_after,
                output_field=DateTimeField()
            )
        )

    def filter_unexpired(self) -> QuerySet:
        """Return QuerySet object that contains only unexpired codes"""
        return self.annotate_expires_at().filter(
            is_used=False,
            expires_at__gt=timezone.now(),
            _tries__lt=self.model.max_tries
        )

    def filter_expired(self) -> QuerySet:
        """Return QuerySet object that contains only expired codes"""
        return self.annotate_expires_at().filter(
            Q(is_used=True) |
            Q(expires_at__lte=timezone.now()) |
            Q(_tries__gte=self.model.max_tries)
        )
