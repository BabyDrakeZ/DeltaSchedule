from typing import List
from django.db.transaction import Atomic
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import generic
from django.http import HttpRequest, Http404
from django.db.models import QuerySet
# Create your views here.
from datetime import date, timedelta, datetime
from .models import Task, Shift
from .forms import ShiftForm

from plotly.offline import plot
import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd

class CalandarView(generic.ListView):
    model = Task
    template_name = "schedule/calendar.html"

def refresh_tasks_view(request:HttpRequest, call):
    if request.method == "POST":
        data = request.POST.copy()
        _date = data.get('date')
        print("_date")

def generate_tasks_from_calls(call_list: List[str], start=None):
    """If start_date is not given auto-fill the start of the month"""
    shift_list: List[Shift] = []
    if not start:
        today = datetime.today()
        start = datetime.combine(date(today.year, today.month, 1),today.time(),today.tzinfo)
    day = 0
    with Atomic():
        for call in call_list:
            shift_list.append(Shift.objects.get(call=call))
    for shift in shift_list:
        new_tasks, days = shift.create_tasks(start + timedelta(days))
        day += days

def availablility(task_list: List[Task]):
    if len(task_list) == 0: #empty
        raise Exception("No tasks to refrence")
    last_task = task_list[0]
    for task in task_list:
        if not isinstance(task, Task):
            raise Exception("Invalid Task type")
        if task.intensity > 2:
            #not available
            pass
        else:
            #available
            pass
        
def calendar_view(request):
    qs = Task.objects.all()
    
    template = "calendar.html"
    if request.method == "POST":
        form = ShiftForm(request.POST)
        if form.is_valid():
            preset:Shift = form.cleaned_data.get('preset')
            date = form.cleaned_data.get('date')
            preset.create_tasks(date)
    else:
        form = ShiftForm()

    tasks_data = [
        dict(Task=str(task), Person=str(task.owner.username), Start=task.start_date, Finish=task.end_date, Call=task.preset.call, Intensity=task.intensity, Delete=f"<a href='{task.pk}/delete'>x</a>") for task in qs
    ]
    # month_of_dates = []
    # d = date.today()
    # focus_month = d.month
    # while (d.month == focus_month):
    #     month_of_dates.append(d)
    #     d = (d + timedelta(1))
    if len(tasks_data) == 0:
        context = {'plot_div': "No Data Provided", 'form':form}
        return render(request,template, context)

    _dataframe = pd.DataFrame(tasks_data)
    fig = px.timeline(_dataframe, x_start="Start", x_end="Finish", y="Person", color="Call",hover_data=["Intensity", "Delete"])
    fig.update_traces(width=0.2,)
    gantt = fig.to_html()
    
    context = {'plot_div': gantt, 'form':form}
    return render(request,template, context)