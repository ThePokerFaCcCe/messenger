from django.utils.functional import cached_property


class NestedViewMixin:

    nested_queryset = None
    """QuerySet that used for getting 
    `nested_object` property"""

    nested_lookup_field = None
    """lookup that used for filtering 
    `queryset` by nested kwarg value"""
    nested_lookup_url_kwarg = None
    """url kwarg that exists in kwargs. e.g.:
    
    `users/<this_kwarg>/shoes/<not_this>`"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.nested_lookup_url_kwarg:
            self.nested_lookup_url_kwarg = self.nested_lookup_field

    def get_queryset(self):
        qs = super().get_queryset()

        lookup = self.nested_lookup_field
        assert lookup is not None, (
            "You should set `nested_lookup_field`"
            f"attribute in {self.__class__.__name__}"
        )

        return qs.filter(**{lookup: self.__nested_kwarg_value})

    @cached_property
    def __nested_kwarg_value(self):
        """Find nested kwarg value in url kwargs"""
        return self.kwargs.get(
            self.nested_lookup_url_kwarg
        )

    def get_nested_queryset(self):
        """retuns QuerySet that used for
        getting `nested_object` property"""

        qs = self.nested_queryset
        assert qs is not None, (
            "You should set `nested_queryset`"
            f"attribute in {self.__class__.__name__}"
            "Or override `get_nested_queryset` method"
        )
        return qs

    @cached_property
    def nested_object(self):
        return self.get_nested_queryset().filter(
            pk=self.__nested_kwarg_value).first()
