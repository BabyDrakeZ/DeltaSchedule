from django.shortcuts import render, redirect
from django.views import generic
from django.http import HttpRequest, Http404
# Create your views here.
from datetime import date
from .models import Task, Preset

from plotly.offline import plot
import plotly.express as px
import pandas as pd

class CalandarView(generic.ListView):
    model = Task
    template_name = "schedule/calendar.html"

def refreshTasks(request:HttpRequest, slug):
    if request.method == "POST":
        data = request.POST.copy()
        _date = data.get('date')
        print("_date")
        

def calendar_view(request):
    qs = Task.objects.all()
    tasks_data = [
        dict(Task=str(task), Owner=str(task.owner.username), Start=task.start_date, Finish=task.end_date) for task in qs
    ]
    if len(tasks_data) == 0:
        context = {'plot_div': "No Data Provided"}
        return render(request,"calendar.html", context)

    df = pd.DataFrame(tasks_data)
    fig = px.timeline(df, x_start="Start", x_end="Finish", y="Owner")
    gantt = fig.to_html()
    context = {'plot_div': gantt}
    return render(request,"calendar.html", context)