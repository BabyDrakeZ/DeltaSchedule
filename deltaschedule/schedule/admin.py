from django.contrib import admin
from .models import Task, TimeBlock, Shift, Schedule, WorkKey
from .forms import *
# Register your models here.

class TimeBlockInline(admin.TabularInline):
    model = TimeBlock
    extra = 2

@admin.register(WorkKey)
class WorkKeyAdmin(admin.ModelAdmin):
    model = WorkKey
    form = WorkKeyForm

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    model = Schedule

@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    model = Shift
    inlines = [TimeBlockInline]

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    model = Task
    form = TaskForm