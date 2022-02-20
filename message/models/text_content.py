from django.db import models
from django.utils.translation import gettext_lazy as _


class TextContent(models.Model):
    text = models.TextField(_("Text"))
