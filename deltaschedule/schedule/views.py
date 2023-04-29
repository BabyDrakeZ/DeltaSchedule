from django.shortcuts import render, redirect
from django.views import generic
from django.http import HttpRequest, Http404
# Create your views here.
from datetime import date
from .models import Task, Preset

class CalandarView(generic.ListView):
    model = Task
    template_name = "schedule/calendar.html"

def refreshTasks(request:HttpRequest, slug):
    if request.method == "POST":
        data = request.POST.copy()
        _date = data.get('date')
        print("_date")
        

def inedex(request):
    qs = Task.objects.all()
    tasks_data = [
        {
            ''
        }
    ]