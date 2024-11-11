from django.contrib import admin
from .models import Survey, Question, Choice

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1

@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_at', 'current_responses')
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'description']
    inlines = [QuestionInline]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'survey', 'question_type', 'created_at')
    list_filter = ['survey', 'question_type']
    search_fields = ['question_text']
    inlines = [ChoiceInline]

@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('choice_text', 'question', 'votes')
    list_filter = ['question']
    search_fields = ['choice_text']