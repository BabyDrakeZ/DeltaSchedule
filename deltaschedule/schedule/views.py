from typing import List
from django.db.transaction import Atomic
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import generic
from django.http import HttpRequest, Http404
from django.db.models import QuerySet
# Create your views here.
from datetime import date, timedelta, datetime
from .models import Task, Shift, TimeBlock, Schedule
from .forms import ShiftForm

from plotly.offline import plot
import plotly.express as px
import pandas as pd

class CalandarView(generic.ListView):
    model = Task
    template_name = "schedule/calendar.html"

def refresh_tasks_view(request:HttpRequest, call):
    if request.method == "POST":
        data = request.POST.copy()
        _date = data.get('date')
        print("_date")
        
def bulk_schedule(request, pk):
    if request.method == "POST":
        data = request.POST.copy()
        call_strs: str = data.get("calls",None)
        start_day = data.get("day", None)
        calls = call_strs.split(",")
        try:
            schedule = Schedule.objects.get(owner=request.user)
        except:
            return render(request, "bulk_form.html", {"message":"You do not have a schedule associated with your account"})
        schedule.generate_tasks_from_calls(calls, start=start_day)
    return render(request,"bulk_form.html")

def schedule_form(request):
    """View for scheduling new tasks"""
    shiftform = ShiftForm(request.POST)
def index(request):
    """View for displaying all schedules"""
    context = {}
    today = date.today()
    if today.month == 2 and ((today.year % 400 == 0) and (today.year % 100 == 0)) or ((today.year % 4 == 0) and (today.year % 100 != 0)):
        num_days = 29
    else:
        month_days = {1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}
        num_days = month_days[today.month]
    context["today"] = today
    context["days"] = range(1, num_days+1)
    schedule_dict = {}
    for schedule in Schedule.objects.all():
        task_list = []
        for task in schedule.tasks.filter(start_date__month=today.month):
            task_list.append(task)
        schedule_dict.update({str(schedule):task_list})
    context["schedule_dict"] = schedule_dict.items()
    return render(request,"calendar.html", context)