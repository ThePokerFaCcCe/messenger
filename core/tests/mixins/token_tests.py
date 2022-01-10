from unittest.mock import patch
from django.db.models.base import Model
from abc import ABC, abstractmethod


class TokenTest(ABC):
    """Tests for BaseToken class"""
    model: Model = None
    @abstractmethod
    def create_instance(self): ...

    def __create_instance(self, *args, **kwargs):
        return self.create_instance()

    @property
    def __model(self):
        assert self.model is not None, (
            "`model` attr must set for %s" % self.__class__.__name__)

        return self.model

    def test_token_hashed(self):
        with patch.object(self.__model, 'should_generate_token',
                          return_value=True):
            instance = self.__create_instance()
            self.assertNotEqual(instance._token_length, len(instance.token))

    def test_encrypted_token(self):
        with patch.object(self.__model, 'should_generate_token',
                          return_value=True):
            instance = self.__create_instance()
            self.assertIsNotNone(instance.encrypted_token)
            self.assertNotEqual(instance.encrypted_token, instance.token)

    def test_find_token(self):
        with patch.object(self.__model, 'should_generate_token',
                          return_value=True):
            instance = self.__create_instance()
            self.assertEqual(instance,
                             self.__model.objects.find_token(instance.encrypted_token))

            instance_2 = self.__create_instance()
            self.assertNotEqual(instance_2,
                                self.__model.objects.find_token(instance.encrypted_token))
