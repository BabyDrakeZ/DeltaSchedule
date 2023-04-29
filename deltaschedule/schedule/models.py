from django.db import models
from typing import Tuple
from datetime import datetime, timedelta, date
from django.contrib.auth.models import User
# Create your models here.
import pandas as pd
from plotly.offline import plot
import plotly.express as px


class Preset(models.Model):
    """Preset of TimeBlocks, takes a start_date and fills in the times from it (creating scheudleblocks)"""
    slug = models.SlugField("Call String", max_length=7, unique=True, primary_key=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    context = models.CharField(max_length=255, default="", blank=True)

    

    INTENSITY_DEF = ((0, "OFF"),(1, "SLEEP"),(2, "WORK"),(3, "WORK+"),(4, "up-OVERNIGHT"),(5, "OVERNIGHT"))

    intensity = models.PositiveIntegerField(default=0, choices=INTENSITY_DEF)

    linked = models.OneToOneField("preset", null=True, blank=True, unique=False, related_name="+", on_delete=models.SET_NULL)
    
   
    def create_tasks(self, set_date:date):
        for block in self.blocks.all():
            if not isinstance(block, TimeBlock):
                raise Exception(f"Expected TimeBlocks not {type(block)}s")
            start_date, end_date = block.get_datetimes(set_date)
            task, created = Task.objects.get_or_create(preset=self,timeblock=block,owner=self.owner,start_date=start_date,end_date=end_date)
        if self.linked and self.linked != self:
            self.linked.create_tasks(end_date.date())
    
    def validate_linked(self):
        """linked cannot be self"""
        if self.linked and self.linked.pk == self.pk:
            raise Exception(f"linked cannot be self")

    def clean(self) -> None:
        self.validate_linked()
        return super().clean()

    def __str__(self) -> str:
        return f"{self.slug} - {self.owner.username} ({self.get_intensity_display()})"
class TimeBlock(models.Model):
    """Allows for naive time objects stetching across days"""
    preset = models.ForeignKey(Preset, related_name='blocks', on_delete=models.CASCADE)
    days = models.SmallIntegerField("Stetched Days", default=0, help_text="Does this timeblock cross days")
    start_time = models.TimeField(auto_now=False, auto_now_add=False)
    end_time = models.TimeField(auto_now=False, auto_now_add=False)

    def validate_start_end(self):
        if (self.days == 0 and not self.end_time > self.start_time):
            raise ValueError("Timeblock end must be later than start. (or days > 0)")

    def clean(self) -> None:
        self.validate_start_end()
        return super().clean()

    def get_timedelta(self):
        if (self.days == 0):
            return  self.end_time - self.start_time
        else:
            hours_till_day = timedelta(days=1) - self.start_time
            hours_after_day = self.end_time
            return timedelta(self.days-1, hours=hours_till_day+hours_after_day)

    def get_datetimes(self, _date:date):
        start_date = datetime.combine(_date, self.start_time)
        end_date = datetime.combine(_date, self.end_time) + timedelta(days=self.days)
        return (start_date, end_date)

class Task(models.Model):
    preset = models.ForeignKey(Preset, null=True, related_name='tasks', on_delete=models.CASCADE)
    timeblock = models.ForeignKey(TimeBlock, null=True, on_delete=models.SET_NULL)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    week_number = models.CharField(max_length=2, blank=True) #defines whether mon, tues, weds, thurs, fri, sat, sun
    start_date = models.DateTimeField(auto_now=False, auto_now_add=False)
    end_date = models.DateTimeField(auto_now=False, auto_now_add=False)

    def get_times(self):
        return self.times
    def __str__(self):    
        return f"{self.owner} ({self.start_date})"
    def save(self, *args, **kwargs):
        if self.week_number == "" or self.week_number == None:
            self.week_number = self.start_date.isocalendar()[1]
        super().save(*args, **kwargs)
