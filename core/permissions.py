from rest_framework import permissions


class IsAdminUserOR(permissions.IsAdminUser):
    """IsAdminUser perm but can be used for (or) statements"""

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request=request, view=view)


class IsOwnerOfItem(permissions.BasePermission):
    def has_object_permission(self, req, view, obj):
        if not (hasattr(req, 'user') and
                req.user.is_authenticated):
            return False

        obj_user = obj

        if hasattr(obj, 'user'):
            obj_user = obj.user
        elif hasattr(obj, 'owner'):
            obj_user = obj.owner
        elif hasattr(obj, 'sender'):
            obj_user = obj.sender

        return obj_user == req.user
