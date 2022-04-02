from django.db.models import QuerySet
from .models import Contact


def get_user_contacts(user_id) -> QuerySet:
    """
    Return queryset of user's contacts
    that 'contacted_user' is selected
    """
    return Contact.objects.select_related("contacted_user")\
        .filter(user_id=user_id)
