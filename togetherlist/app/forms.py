from django import forms
from django.contrib.auth.models import User


class TrackForm(forms.Form):
    def __init__(self, *args, choices=[], **kwargs):
        super(TrackForm, self).__init__(*args, **kwargs)
        self.fields['Your top tracks'] =  forms.MultipleChoiceField(choices=choices, widget=forms.CheckboxSelectMultiple)

# class TrackForm(forms.ModelForm):
#     class Meta:
#         model = Track
#         fields = ['title', 'artist_names']

# class TrackForm(forms.ModelForm):
#     class Meta:
#         model = TrackModel

#     def __init__(self, *args, **kwargs):
#         super(TrackForm, self).__init__(*args, **kwargs)
#         self.fields['tracks'] =  forms.ChoiceField(queryset=TrackModel.objects.all(), empty_label="Choose tracks",)

# class TrackForm(forms.Form):
#     track_choices = [
#         ('RR', 'Never Gonna Give You Up'),
#         ('RA', 'Some Other Song')
#     ]
#     #choice = forms.ChoiceField(choices=track_choices, widget=forms.RadioSelect)
#     tracks = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=track_choices)

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