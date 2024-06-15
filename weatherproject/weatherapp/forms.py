from django import forms

class CityForm(forms.Form):
    name = forms.CharField(max_length=100)
    country = forms.CharField(max_length=2, required=False, label="Country Code (optional)")
