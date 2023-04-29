from django.shortcuts import render
from django.views import generic
# Create your views here.

from .models import Task

class CalandarView(generic.ListView):
    model = Task
    template_name = "schedule/calendar.html"


def inedex(request):
    qs = Task.objects.all()
    tasks_data = [
        {
            ''
        }
    ]