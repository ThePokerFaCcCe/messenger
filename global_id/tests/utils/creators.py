from uuid import uuid4
from ..models.fake_chat import FakeChat

from user.tests.utils import create_user
from global_id.models import GUID


def generate_guid_string() -> str:
    return f'a{uuid4().hex[:10]}'


def create_guid(guid=None, obj=None, **kwargs) -> GUID:
    guid = guid if guid else generate_guid_string()
    obj = obj if obj else create_user()
    return GUID.objects.create(guid=guid, chat=obj, **kwargs)


def create_fake_chat() -> FakeChat:
    return FakeChat.objects.create()
