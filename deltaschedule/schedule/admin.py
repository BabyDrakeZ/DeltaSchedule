from django.contrib import admin
from .models import Task, TimeBlock
# Register your models here.

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    model = Task