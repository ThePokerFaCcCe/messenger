# COPYRIGHT: Used codes of DjangoRestFramework permissions
# https://github.com/encode/django-rest-framework/blob/master/rest_framework/permissions.py

class OperationHolderMixin:
    def __and__(self, other):
        return OperandHolder(AND, self, other)

    def __or__(self, other):
        return OperandHolder(OR, self, other)

    def __rand__(self, other):
        return OperandHolder(AND, other, self)

    def __ror__(self, other):
        return OperandHolder(OR, other, self)

    def __invert__(self):
        return SingleOperandHolder(NOT, self)


class SingleOperandHolder(OperationHolderMixin):
    def __init__(self, operator_class, op1_class):
        self.operator_class = operator_class
        self.op1_class = op1_class

    def __call__(self, *args, **kwargs):
        op1 = self.op1_class(*args, **kwargs)
        return self.operator_class(op1)


class OperandHolder(OperationHolderMixin):
    def __init__(self, operator_class, op1_class, op2_class):
        self.operator_class = operator_class
        self.op1_class = op1_class
        self.op2_class = op2_class

    def __call__(self, *args, **kwargs):
        op1 = self.op1_class(*args, **kwargs)
        op2 = self.op2_class(*args, **kwargs)
        return self.operator_class(op1, op2)


class AND:
    def __init__(self, op1, op2):
        self.op1 = op1
        self.op2 = op2

    def has_permission(self, scope, consumer):
        return (
            self.op1.has_permission(scope, consumer) and
            self.op2.has_permission(scope, consumer)
        )

    def has_object_permission(self, scope, consumer, obj):
        return (
            self.op1.has_object_permission(scope, consumer, obj) and
            self.op2.has_object_permission(scope, consumer, obj)
        )


class OR:
    def __init__(self, op1, op2):
        self.op1 = op1
        self.op2 = op2

    def has_permission(self, scope, consumer):
        return (
            self.op1.has_permission(scope, consumer) or
            self.op2.has_permission(scope, consumer)
        )

    def has_object_permission(self, scope, consumer, obj):
        return (
            self.op1.has_object_permission(scope, consumer, obj) or
            self.op2.has_object_permission(scope, consumer, obj)
        )


class NOT:
    def __init__(self, op1):
        self.op1 = op1

    def has_permission(self, scope, consumer):
        return not self.op1.has_permission(scope, consumer)

    def has_object_permission(self, scope, consumer, obj):
        return not self.op1.has_object_permission(scope, consumer, obj)


class BasePermissionMetaclass(OperationHolderMixin, type):
    pass


class BasePermission(metaclass=BasePermissionMetaclass):
    """
    A base class from which all permission classes should inherit.
    """

    def has_permission(self, scope, consumer):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return True

    def has_object_permission(self, scope, consumer, obj):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return True


class IsAuthenticated(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, scope, consumer):
        user = scope.user
        return bool(user and user.is_authenticated)


class IsAdminUser(BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, scope, consumer):
        return bool(scope.user and scope.user.is_staff)
