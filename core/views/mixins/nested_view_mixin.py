
class NestedViewMixin:

    nested_lookup_field = None
    nested_lookup_url_kwarg = None
    """url kwarg that exists in kwargs. e.g.:
    
    `users/<this_kwarg>/shoes/<not_this>`"""

    def get_queryset(self):
        qs = super().get_queryset()

        lookup = self.nested_lookup_field
        assert lookup is not None, (
            "You should set `nested_lookup_field`"
            f"attribute in {self.__class__.__name__}"
        )

        url_kwarg = self.nested_lookup_url_kwarg or lookup
        nested_kwarg_value = self.kwargs.get(url_kwarg)

        return qs.filter(**{lookup: nested_kwarg_value})
