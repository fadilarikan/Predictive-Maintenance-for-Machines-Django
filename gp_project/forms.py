from django import forms

class PredictForm(forms.Form):
    vibration_y = forms.FloatField()
    pressure_6h_mean = forms.FloatField()
    temperature_6h_std = forms.FloatField()
