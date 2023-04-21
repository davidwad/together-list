from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class TrackForm(forms.Form):
    def __init__(self, *args, choices=[], **kwargs):
        super(TrackForm, self).__init__(*args, **kwargs)
        self.form_name = 'Tracks'
        self.fields[self.form_name] =  forms.MultipleChoiceField(choices=choices, widget=forms.CheckboxSelectMultiple)
        self.no_of_tracks = settings.N_VOTES

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get(self.form_name) is None or len(cleaned_data.get(self.form_name)) != self.no_of_tracks:
            raise ValidationError('Exactly {} tracks must be selected'.format(self.no_of_tracks))


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']


class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
                'username', 
                'password'
        ]
