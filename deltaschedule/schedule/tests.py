from django.test import TestCase
from datetime import time, datetime, date
# Create your tests here.
from django.contrib.auth.models import User
from .models import TimeBlock, Shift, Task, Schedule

class PresetModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="TestUser", password="pbkdf2_sha")
        schedule = Schedule.objects.create(owner=cls.user)
        linked = Shift(call="PC", schedule=schedule, context="sleep recovery", intensity=5, linked=None)
        linked.save()
        TimeBlock.objects.create(schedule=linked, start_time=time(7, 2), end_time=time(14, 2))
        overnight = Shift(call="N1", schedule=schedule, context="overnight", intensity=4, linked=linked)
        overnight.save()
        TimeBlock.objects.create(schedule=overnight, start_time=time(7,1), end_time=time(12,1))
        TimeBlock.objects.create(schedule=overnight, start_time=time(19,00), end_time=time(7,0))
        backup = Shift(call="N2", schedule=schedule, context="Backup Night", intensity=3, linked=linked)
        TimeBlock.objects.create(schedule=overnight, start_time=time(7,1), end_time=time(12,1))
        TimeBlock.objects.create(schedule=overnight, start_time=time(19,00), end_time=time(7,0))
        

        cls.overnight = overnight
        cls.linked = linked

    def test_create_tasks(self):
        assert Task.objects.count() == 0
        #setup
        time1 = time(7, 1)
        time2 = time(12,1)
        time3 = time(19,0)
        time4 = time(7,0)
        block12 = TimeBlock(schedule=self.schedule, start_time=time1, end_time=time2)
        block34 = TimeBlock(schedule=self.schedule, days=1, start_time=time3, end_time=time4)
        block12.save()
        block34.save()
        _date = date.today()
        print(_date)
        self.schedule.create_tasks(_date)
        assert Task.objects.count() == 3
        assert Task.objects.filter(end_date__day__gt=_date.day).count() == 2
        #teardown