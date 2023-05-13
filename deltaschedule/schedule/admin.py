from django.contrib import admin
from .models import Task, TimeBlock, Shift
# Register your models here.

class TimeBlockInline(admin.TabularInline):
    model = TimeBlock
    extra = 2

@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    model = Shift
    inlines = [TimeBlockInline]

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    model = Task