from rest_framework.routers import DynamicRoute, Route, DefaultRouter
from rest_framework_nested.routers import NestedMixin


class NoLookupRouter(DefaultRouter):
    """DefaultRouter without {lookup} in urls.

    list and detail viewsets should have different prefixes
    """
    routes = [
        # List route.
        Route(
            url=r'^{prefix}{trailing_slash}$',
            mapping={
                'get': 'list',
                'post': 'create'
            },
            name='{basename}-list',
            detail=False,
            initkwargs={'suffix': 'List'}
        ),
        # Dynamically generated list routes. Generated using
        # @action(detail=False) decorator on methods of the viewset.
        DynamicRoute(
            url=r'^{prefix}/{url_path}{trailing_slash}$',
            name='{basename}-{url_name}',
            detail=False,
            initkwargs={}
        ),
        # Detail route.
        Route(
            url=r'^{prefix}{trailing_slash}$',
            mapping={
                'get': 'retrieve',
                'put': 'update',
                'patch': 'partial_update',
                'delete': 'destroy'
            },
            name='{basename}-detail',
            detail=True,
            initkwargs={'suffix': 'Instance'}
        ),
        # Dynamically generated detail routes. Generated using
        # @action(detail=True) decorator on methods of the viewset.
        DynamicRoute(
            url=r'^{prefix}/{url_path}{trailing_slash}$',
            name='{basename}-{url_name}',
            detail=True,
            initkwargs={}
        ),
    ]


class NoLookupNestedMixin:
    # from rest_framework_nested.routers import NestedMixin

    def __init__(self, parent_router, parent_prefix, *args, **kwargs):
        self.parent_router = parent_router
        self.parent_prefix = parent_prefix

        super().__init__(*args, **kwargs)

        if 'trailing_slash' not in kwargs:
            self.trailing_slash = parent_router.trailing_slash

        parent_registry = [registered for registered
                           in self.parent_router.registry
                           if registered[0] == self.parent_prefix]
        try:
            parent_registry = parent_registry[0]
            parent_prefix, parent_viewset, parent_basename = parent_registry
        except:
            raise RuntimeError('parent registered resource not found')

        nested_routes = []

        self.parent_regex = '{parent_prefix}/'.format(
            parent_prefix=parent_prefix,
        )

        if not self.parent_prefix and self.parent_regex[0] == '/':
            self.parent_regex = self.parent_regex[1:]
        if hasattr(parent_router, 'parent_regex'):
            self.parent_regex = parent_router.parent_regex + self.parent_regex

        for route in self.routes:
            route_contents = route._asdict()

            escaped_parent_regex = self.parent_regex.replace('{', '{{').replace('}', '}}')

            route_contents['url'] = route.url.replace('^', '^' + escaped_parent_regex)
            nested_routes.append(type(route)(**route_contents))

        self.routes = nested_routes


class NestedNoLookupRouter(NoLookupNestedMixin, NoLookupRouter):
    """Nested router for NoLookupRouter"""
    pass


class NestedJustFirstLookupRouter(NestedMixin, NoLookupRouter):
    """Nested no lookup router that only contains parent lookup"""
    pass
