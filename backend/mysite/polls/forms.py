from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Question, Choice, Survey

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        label='ユーザー名',
        widget=forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'})
    )
    password1 = forms.CharField(
        label='パスワード',
        widget=forms.PasswordInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'})
    )
    password2 = forms.CharField(
        label='パスワード（確認）',
        widget=forms.PasswordInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'})
    )

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'question_type', 'is_required', 'order']

    def clean(self):
        cleaned_data = super().clean()
        print(f"Validating question form: {cleaned_data}")  # デバッグ用
        return cleaned_data

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['choice_text', 'order']

    def clean(self):
        cleaned_data = super().clean()
        print(f"Validating choice form: {cleaned_data}")  # デバッグ用
        return cleaned_data

class SurveyForm(forms.ModelForm):
    class Meta:
        model = Survey
        exclude = ['status', 'current_responses']