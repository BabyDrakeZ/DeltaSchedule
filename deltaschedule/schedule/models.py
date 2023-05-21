from typing import List, Union
from django.db import models, transaction
from colorfield.fields import ColorField
from typing import Tuple
from datetime import datetime, timedelta, date, time
from django.contrib.auth.models import User
from copy import deepcopy
# Create your models here.
import pandas as pd
from plotly.offline import plot
import plotly.express as px


WORK_KEYS = ((0, "OFF"),(1, "WORK"),(2, "SLEEP"),(3,"BACKUP"),(4, "OVERNIGHT"))

class Schedule(models.Model):
    """Schedule is free to work when dependent is avaiable"""
    name = models.CharField(max_length=30, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    dependent = models.ForeignKey("schedule", on_delete=models.SET_NULL, related_name="dependents", null=True, blank=True)
    available_at = models.PositiveIntegerField(default=1, choices=WORK_KEYS, help_text="defines the maximum level of work that you are avaible at")
    
    def to_html(self):
        qs: models.QuerySet[Task] = self.tasks.all()
        tasks_data = [
            dict(Task=str(task), y=self.__str__(), Schedule=self.__str__(), Start=task.start_date, Finish=task.end_date, Call=task.preset.call, Intensity=task.intensity, Delete=f"<a href='{task.pk}/delete'>x</a>") for task in qs
        ]
        
        _dataframe = pd.DataFrame(tasks_data)
        if (_dataframe.empty): return "No Task Data to Display"
        fig = px.timeline(_dataframe, x_start="Start", x_end="Finish", y="y", color="Call",hover_data=["Intensity", "Delete"])
        fig.update_traces(width=0.2,)
        gantt = fig.to_html()
        return gantt
    
    def __str__(self):
        if self.name:
            return self.name
        else:
            return self.owner.username
    
    def dependent_availability(self):
        """When dependent is working overnight, you are not available, visa versa"""
        dependent: Schedule = self.dependent
        if dependent == None:
            raise Exception("dependent_availability() can only be run on schedules which are dependent")
        dependent_task_list: List[Task] = dependent.tasks.all().list()
        new_task_list: List[Task] = []
        for task in dependent_task_list:
            if task.intensity > 1:
                #not available to work (staying at home)
                off_task = Task.objects.get_or_create(intensity=1, context="Off Work", timeblock=task.timeblock, start_date=task.start_date, schedule=self)
                new_task_list.append(off_task)
            else:
                #available to work
                block = TimeBlock.objects.get_or_create(start_time=time(0,0), end_time=time(12,0))[0]
                on_task = Task.objects.get_or_create(intensity=2, context="Available to work", timeblock=block, schedule=self, start_date=task.start_date)
                new_task_list.append(on_task)
    def generate_tasks_from_calls(self, call_list: List[str], start=None):
        """If start_date is not given auto-fill the start of the month"""
        if not start:
            today = datetime.today()
            start = datetime.combine(date(today.year, today.month, 1),today.time(),today.tzinfo)
        day = 0
        for shift in Shift.objects.filter(call__in=call_list, schedule=self):
            new_tasks, days = shift.create_tasks(start + timedelta(day))
            day += days

class Shift(models.Model):
    """Preset of TimeBlocks, takes a start_date and fills in the times from it (creating scheudleblocks)"""
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    call = models.SlugField("Call String", max_length=7, unique=True, primary_key=True)
    context = models.CharField(max_length=255, default="", blank=True)
    intensity = models.PositiveIntegerField(default=2, choices=WORK_KEYS)
    color = ColorField()

    linked = models.ForeignKey("shift", null=True, blank=True, unique=False, related_name="+", on_delete=models.SET_NULL)
    
    def create_tasks(self, set_date: Union[date, datetime]):
        if isinstance(set_date, datetime):
            set_date = set_date.date()
        block:TimeBlock
        created_tasks: List[Task] = []
        days = 1
        for block in self.blocks.all():
            start_date, end_date = block.get_datetimes(set_date)
            task, created = Task.objects.get_or_create(preset=self,timeblock=block,schedule=self.schedule,start_date=start_date,)
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
        call = self.call
        try:
            self.refresh_from_db(fields=['call'])
        except: pass
        old_call = self.call
        if call != old_call:
            copy = deepcopy(self)
            copy.call = call
            copy.pk = call
            super(Shift, copy).save(*args, **kwargs)
            self.blocks.update(preset=copy)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.call} - {self.schedule.__str__()} ({self.get_intensity_display()})"

class TimeBlock(models.Model):
    """Allows for naive time objects stetching across days"""
    schedule = models.ForeignKey(Shift, related_name='blocks', null=True, blank=True, unique=False, on_delete=models.SET_NULL)
    days = models.SmallIntegerField("Stetched Days", default=0, help_text="(autofills 1 if start > end)")
    start_time = models.TimeField(auto_now=False, auto_now_add=False)
    end_time = models.TimeField(auto_now=False, auto_now_add=False)
    order = models.PositiveSmallIntegerField(default=0) #if multiple time blocks on a Shift, choose which one

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
        ordering = ['order','start_time']

class Task(models.Model):
    preset = models.ForeignKey(Shift, null=True, related_name='tasks', blank=True, on_delete=models.CASCADE)
    timeblock = models.ForeignKey(TimeBlock, models.CASCADE, related_name='+',)
    schedule = models.ForeignKey(Schedule, related_name='tasks', on_delete=models.CASCADE)
    week_number = models.CharField(max_length=2, blank=True) #defines whether mon, tues, weds, thurs, fri, sat, sun
    start_date = models.DateField(auto_now=False, auto_now_add=False)
    context = models.CharField(max_length=255, default="", blank=True)
    intensity = models.SmallIntegerField(default=2, choices=WORK_KEYS)
    color = ColorField()

    @property
    def end_date(self):
        return self.get_datetimes()[1]

    def get_datetimes(self):
        """Returns datetime tuple (start, end)"""
        return self.timeblock.get_datetimes(self.start_date)
    @property
    def start_datetime(self):
        return self.get_datetimes()[0]
    @property
    def end_datetime(self):
        return self.get_datetimes()[1]


    def get_times(self):
        return self.times
    def __str__(self):    
        return f"{self.schedule} ({self.start_date})"
    def save(self, *args, **kwargs):
        if self.preset != None:
            self.intensity = self.preset.intensity
        if self.week_number == "" or self.week_number == None:
            self.week_number = self.start_date.isocalendar()[1]
        super().save(*args, **kwargs)


def import_presets():
    pass