from typing import List, Union
from django.db import models
from typing import Tuple
from datetime import datetime, timedelta, date
from django.contrib.auth.models import User
from copy import deepcopy
# Create your models here.
import pandas as pd
from plotly.offline import plot
import plotly.express as px

class Schedule(models.Model):
    """Doctor's is preassigned with call numbers. Pilot's is dependent on doctor schedule (schedule when Doctor is available), Baby Sitter is dependent on both schedules (schedule when Doctor and Pilot are not free)"""
    doctor = models.OneToOneField(User, related_name="doctor_schedule", null=True, on_delete=models.SET_NULL)
    pilot = models.OneToOneField(User, related_name="pilot_schedule", null=True, on_delete=models.SET_NULL)
    babysitter = models.OneToOneField(User, related_name="sitter_schedule", null=True, on_delete=models.SET_NULL)

INTENSITY_DEF = ((0, "OFF"),(1, "WORK1"),(2, "WORK2"),(3, "SLEEP"),(4, "OVERNIGHT-bk"),(5, "OVERNIGHT"), (6, "OVERNIGHT-24"))
class Shift(models.Model):
    """Preset of TimeBlocks, takes a start_date and fills in the times from it (creating scheudleblocks)"""
    call = models.SlugField("Call String", max_length=7, unique=True, primary_key=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    context = models.CharField(max_length=255, default="", blank=True)

    intensity = models.PositiveIntegerField(default=2, choices=INTENSITY_DEF)

    linked = models.ForeignKey("shift", null=True, blank=True, unique=False, related_name="+", on_delete=models.SET_NULL)
    
    def create_tasks(self, set_date: Union[date, datetime]):
        if isinstance(set_date, datetime):
            set_date = set_date.date()
        block:TimeBlock
        created_tasks: List[Task] = []
        days = 1
        for block in self.blocks.all():
            start_date, end_date = block.get_datetimes(set_date)
            task, created = Task.objects.get_or_create(preset=self,timeblock=block,owner=self.owner,start_date=start_date,end_date=end_date)
            created_tasks.append(task)
            days += block.days
        if self.linked and self.linked != self:
            _tasks, _days = self.linked.create_tasks(end_date.date())
            created_tasks.append(_tasks)
            days += _days
        return (created_tasks, days)
    def days_spanned(self):
        blocks: models.QuerySet[TimeBlock] = self.blocks.all()

    def validate_linked(self):
        """linked cannot be self"""
        if self.linked and self.linked.pk == self.pk:
            raise Exception(f"linked cannot be self")

    def clean(self) -> None:
        self.validate_linked()
        return super().clean()

    def save(self, *args, **kwargs):
        slug = self.call
        try:
            self.refresh_from_db(fields=['slug'])
        except: pass
        slug_old = self.call
        if slug != slug_old:
            copy = deepcopy(self)
            copy.call = slug
            copy.pk = slug
            super(Shift, copy).save(*args, **kwargs)
            self.blocks.update(preset=copy)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.call} - {self.owner.username} ({self.get_intensity_display()})"
class TimeBlock(models.Model):
    """Allows for naive time objects stetching across days"""
    preset = models.ForeignKey(Shift, related_name='blocks', unique=False, on_delete=models.CASCADE)
    days = models.SmallIntegerField("Stetched Days", default=0, help_text="(autofills 1 if start > end)")
    start_time = models.TimeField(auto_now=False, auto_now_add=False)
    end_time = models.TimeField(auto_now=False, auto_now_add=False)
    order = models.PositiveSmallIntegerField() #if multiple time blocks on a Shift, choose which one

    def fix_days(self):
        if (self.days == 0 and self.start_time < self.end_time):
            self.days = 1

    def clean(self) -> None:
        self.fix_days()
        return super().clean()

    def get_timedelta(self):
        if (self.days == 0):
            return  self.end_time - self.start_time
        else:
            hours_till_day = timedelta(days=1) - self.start_time
            hours_after_day = self.end_time
            return timedelta(self.days-1, hours=hours_till_day+hours_after_day)

    def get_datetimes(self, start_date:date):
        start_date = datetime.combine(start_date, self.start_time)
        end_date = datetime.combine(start_date, self.end_time) + timedelta(days=self.days)
        return (start_date, end_date)
    
    @classmethod
    def from_datetime_delta(cls, _datetime:datetime, _delta:timedelta):
        """Constructor from _datetime and _delta"""
        start = _datetime
        end = start + _delta
        block = cls(days=0, start_time= start.time(), end_time = end.time())
        block.fix_days()
        block.days += _delta.days
        return block
    @classmethod
    def from_datetime_datetime(cls, start:datetime, end:datetime):
        """Constructor from two datetimes"""
        if end < start:
            raise ValueError("end_date is less than start_date")
        _delta = end - start
        block = cls(days=0, start_time= start.time(), end_time = end.time())
        block.fix_days()
        block.days += _delta.days
        return block

    class Meta:
        ordering = ['start_time']

class Task(models.Model):
    preset = models.ForeignKey(Shift, null=True, related_name='tasks', blank=True, on_delete=models.CASCADE)
    timeblock = models.ForeignKey(TimeBlock, on_delete=models.SET_NULL)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    week_number = models.CharField(max_length=2, blank=True) #defines whether mon, tues, weds, thurs, fri, sat, sun
    start_date = models.DateField(auto_now=False, auto_now_add=False)
    intensity = models.SmallIntegerField(default=2, choices=INTENSITY_DEF)

    def get_datetimes(self):
        """Returns datetime tuple (start, end)"""
        return self.timeblock.get_datetimes(self.start_date)

    def get_times(self):
        return self.times
    def __str__(self):    
        return f"{self.owner} ({self.start_date})"
    def save(self, *args, **kwargs):
        if self.preset != None:
            self.intensity = self.preset.intensity
        if self.week_number == "" or self.week_number == None:
            self.week_number = self.start_date.isocalendar()[1]
        super().save(*args, **kwargs)


def import_presets():
    pass