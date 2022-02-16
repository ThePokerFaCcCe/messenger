from typing import Any, Optional, Type
from django.db.models import Model, Field


def get_field(model: Type[Model], field_name: str
              ) -> Optional[Type[Field]]:
    """Get a field in model by name"""
    for field in model._meta.fields:
        if field.name == field_name:
            return field


def get_field_attr(model: Type[Model], field_name: str,
                   attr_name:  str, default=None
                   ) -> Optional[Any]:
    """Get attr in field in model"""
    if (field := get_field(model, field_name)):
        return getattr(field, attr_name, default)
