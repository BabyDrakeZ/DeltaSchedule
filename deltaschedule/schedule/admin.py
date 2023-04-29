from django.contrib import admin
from .models import Task, TimeBlock, Preset
# Register your models here.

class TimeBlockInline(admin.TabularInline):
    model = TimeBlock
    extra = 2

@admin.register(Preset)
class PresetAdmin(admin.ModelAdmin):
    model = Preset
    inlines = [TimeBlockInline]

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    model = Task