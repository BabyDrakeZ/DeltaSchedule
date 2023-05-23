from django import forms
from .models import WorkKey#,Shift,  Task

class DatePickerInput(forms.DateInput):
    input_type = 'date'

class AddShiftForm(forms.Form):
    #shift = forms.ModelChoiceField(Shift.objects.all().order_by('schedule','call'), required=True)
    date = forms.DateField(widget=DatePickerInput, required=True)

class CreateShiftForm(forms.ModelForm):
    class Meta:
        #model = Shift
        fields = '__all__'

class WorkKeyForm(forms.ModelForm):
    class Meta:
        model = WorkKey
        fields = '__all__'
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
        }
class TaskForm(forms.ModelForm):
    class Meta:
        #model = Task
        fields = '__all__'
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
        }