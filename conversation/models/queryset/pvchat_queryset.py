from django.db.models import QuerySet


class PrivateChatQuerySet(QuerySet):
    def filter(self, *args, **kwargs) -> QuerySet:
        """With this filter, if you assign an iterable for `users`,
        it works like `exact` and returns queryset that contain
        only users with exact list. e.g.:

        `users = [1, 3]` only return queryset of objects that have 
        `[1, 3]` in their `users` field."""

        users = kwargs.pop('users', -1)
        qs = super()
        if (users != -1):
            try:
                # Make sure `users` are iterable
                iter(users)
            except TypeError:
                return super().filter(users=users, *args, **kwargs)

            for user in users:
                qs = qs.filter(users=user)

        qs = qs.filter(*args, **kwargs)
        return qs
