from django.test.testcases import TestCase
from django.core.exceptions import ValidationError
from django.core.cache import cache
from rest_framework.test import APITestCase
from rest_framework import status

from core.tests.mixins import ClearCacheMixin
from auth_app.tests.utils import create_access
from .models import FakeChat
from .utils import (create_guid, GUIDViewCaller,
                    FakeChatViewCaller, create_fake_chat)


class GUIDModelTest(TestCase):

    def test_valid_guid(self):
        invalid_guids = [
            '$Matin_Kh>',
            '_matinkh',
            '0matinkh',
            'matinkh_',
            'matin__kh',
            'matin_kh_n',
            'mat',
            'matin'*120,
        ]

        valid_guids = [
            'matin_khaleghi1381',
            'matin1381kh',
            'matinkhaleghi',
        ]
        for guid in invalid_guids:
            with self.assertRaises(ValidationError):
                create_guid(guid=guid).full_clean()

        for guid in valid_guids:
            create_guid(guid=guid).full_clean()


class GUIDViewTest(APITestCase):
    caller: GUIDViewCaller

    def setUp(self):
        self.caller = GUIDViewCaller(self.client)
        self.access = create_access(
            activate_user=True).encrypted_token

    def test_get_exists_guid(self):
        self.caller.retrieve__get(self.access)

    def test_get_bad_guid(self):
        self.caller.retrieve__get(
            self.access, guid='##%^%^%^&*R%imbad',
            allowed_status=status.HTTP_404_NOT_FOUND)


class GUIDMixinTest(ClearCacheMixin, TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.fchat = create_fake_chat()

    def test_create_update_guid(self):
        new_guid = 'noImGuid'
        self.fchat.guid = 'iamtheguid'
        self.fchat.save()

        self.fchat.guid = new_guid
        self.fchat.save()

        self.fchat.refresh_from_db()
        self.assertEqual(self.fchat.guid, new_guid)

    def test_set_duplicate_guid(self):
        guid = 'imgoodguid'
        fc = create_fake_chat()
        self.fchat.guid = guid
        self.fchat.save()

        try:
            fc.guid = guid
            fc.save()
        except:
            pass
        else:
            self.assert_(False, msg='duplicate guids!')

    def test_delete_guid(self):
        self.fchat.guid = 'iamaguid'
        self.fchat.save()
        del self.fchat.guid
        self.fchat.refresh_from_db()
        self.assertIsNone(self.fchat.guid)

    def test_cache_works(self):
        fchat = create_fake_chat()
        fchat.guid = 'bigchatw'
        fchat.save()

        with self.assertNumQueries(0):
            fchat.guid

        fchat = FakeChat.objects.get(pk=fchat.pk)

        with self.assertNumQueries(0):
            fchat.guid

    def test_cache_update(self):
        guid = 'anotherguid'

        fchat = create_fake_chat()
        fchat.guid = 'bigchatw'
        fchat.save()

        fchat.guid = guid
        fchat.save()

        self.assertEqual(fchat.guid, guid)
        del fchat.guid

        self.assertIsNone(fchat.guid)


class GUIDCRUDMixinTest(ClearCacheMixin, APITestCase):
    caller: FakeChatViewCaller

    def setUp(self):
        super().setUp()
        self.caller = FakeChatViewCaller(self.client)

    def test_get_guid(self):
        self.caller.retrieve__guid()

    def test_set_valid_guid(self):
        fc = create_fake_chat()
        guid = "iamvalid"
        self.caller.post__guid(pk=fc.pk, new_guid=guid)
        fc.refresh_from_db()
        self.assertEqual(fc.guid, guid)

    def test_set_invalid_guid(self):
        self.caller.post__guid(
            new_guid='@##$#bad',
            allowed_status=status.HTTP_400_BAD_REQUEST)

    def test_set_duplicate_guid(self):
        guid = 'iammatin'
        fc = create_fake_chat()
        fc.guid = guid
        fc.save()

        self.caller.post__guid(
            new_guid=guid,
            allowed_status=status.HTTP_400_BAD_REQUEST)

    def test_delete_guid(self):
        fc = create_fake_chat()
        fc.guid = 'iamguid'
        fc.save()
        self.caller.delete__guid(pk=fc.pk)
        cache.clear()
        fc.refresh_from_db()
        self.assertIsNone(fc.guid)
