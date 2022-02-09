from django.test.testcases import TestCase

from .utils import create_group_community


class GroupModelTest(TestCase):
    def test_grouprules_created(self):
        gp = create_group_community()
        self.assertIsNotNone(
            gp.rules, msg='Rules not created')
