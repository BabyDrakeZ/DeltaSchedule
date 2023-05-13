from django import forms
from .models import Shift

class DatePickerInput(forms.DateInput):
    input_type = 'date'

class ShiftForm(forms.Form):
    preset = forms.ModelChoiceField(Shift.objects.all().order_by('slug'), required=True)
    date = forms.DateField(widget=DatePickerInput, required=True)