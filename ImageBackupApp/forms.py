
from django import forms
class ImageForm(forms.Form):  
    file = forms.FileField() # for creating file input  