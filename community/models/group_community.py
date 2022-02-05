from django.db import models, transaction

from .group_rules import GroupRules


class GroupCommunity(models.Model):
    rules = models.OneToOneField(to=GroupRules, on_delete=models.PROTECT,
                                 related_name='group', auto_created=True,
                                 null=True)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self.rules is None:
                self.rules = GroupRules.objects.create()
            return super().save(*args, **kwargs)
