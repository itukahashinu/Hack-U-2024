from django import forms
from .models import Idea, Theme

class IdeaForm(forms.ModelForm):
    class Meta:
        model = Idea
        fields = ['title', 'content', 'theme']

    def __init__(self, *args, **kwargs):
        super(IdeaForm, self).__init__(*args, **kwargs)
        self.fields['theme'].queryset = Theme.objects.all()