from django.db.models import QuerySet


class SoftDeleteQuerySet(QuerySet):
    def filter_deleted(self, *args, **kwargs) -> QuerySet:
        """Filter only in deleted objects"""
        return self.filter(is_deleted=True, *args, **kwargs)

    def filter_not_deleted(self, *args, **kwargs) -> QuerySet:
        """Filter only in not deleted objects"""
        return self.filter(is_deleted=False, *args, **kwargs)
