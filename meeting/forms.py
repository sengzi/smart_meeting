from django import forms

class RadioForm(forms.Form):
    vote=models.integerfield()
    CHOICES = [('voting','Yes'),('F','No')]