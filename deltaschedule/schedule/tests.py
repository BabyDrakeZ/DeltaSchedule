from django.test import TestCase
from datetime import time, datetime, date
# Create your tests here.
from django.contrib.auth.models import User
from .models import TimeBlock, Preset, Task

class PresetModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="TestUser", password="pbkdf2_sha")
        linked = Preset(slug="~PC", owner=cls.user, context="sleep recovery", intensity=1, linked=None)
        linked.save()
        TimeBlock.objects.create(preset=linked, start_time=time(7, 2), end_time=time(14, 2))
        preset = Preset(slug="~N1", owner=cls.user, context="overnight", intensity=5, linked=linked)
        preset.save()
        cls.preset = preset
        cls.linked = linked

    def test_create_tasks(self):
        assert Task.objects.count() == 0
        #setup
        time1 = time(7, 1)
        time2 = time(12,1)
        time3 = time(19)
        time4 = time(7)
        block12 = TimeBlock(preset=self.preset, start_time=time1, end_time=time2)
        block34 = TimeBlock(preset=self.preset, days=1, start_time=time3, end_time=time4)
        block12.save()
        block34.save()
        _date = date.today()
        print(_date)
        self.preset.create_tasks(_date)
        assert Task.objects.count() == 3
        #teardown