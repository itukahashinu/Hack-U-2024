from django.contrib import admin
from .models import Survey, Question, Choice, SurveyResponse, Answer

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3
    fields = ['choice_text', 'order']

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    fields = ['question_text', 'question_type', 'is_required', 'order']
    show_change_link = True

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ['question', 'selected_choices']
    can_delete = False

@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_at', 'start_date', 'end_date', 'required_responses')
    list_filter = ['status', 'created_at', 'start_date', 'end_date']
    search_fields = ['title']
    readonly_fields = ['status']
    fieldsets = [
        (None, {'fields': ['title', 'description']}),
        ('Schedule', {
            'fields': ['start_date', 'end_date', 'required_responses'],
            'description': 'Set the survey schedule and response requirements'
        }),
        ('Status', {
            'fields': ['status'],
            'description': 'Survey status is automatically updated based on dates'
        }),
    ]
    inlines = [QuestionInline]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'survey', 'question_type', 'is_required', 'order')
    list_filter = ['survey', 'question_type', 'is_required']
    search_fields = ['question_text', 'survey__title']
    fields = ['survey', 'question_text', 'question_type', 'is_required', 'order']
    inlines = [ChoiceInline]

@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('choice_text', 'get_survey', 'get_question', 'get_question_type', 'order', 'votes')
    list_filter = ['question__survey', 'question__question_type', 'question']
    search_fields = ['choice_text', 'question__question_text', 'question__survey__title']
    fields = ['question', 'choice_text', 'votes', 'order']

    def get_survey(self, obj):
        return obj.question.survey.title
    get_survey.short_description = 'Survey'
    get_survey.admin_order_field = 'question__survey__title'

    def get_question(self, obj):
        return obj.question.question_text
    get_question.short_description = 'Question'
    get_question.admin_order_field = 'question__question_text'

    def get_question_type(self, obj):
        return obj.question.get_question_type_display()
    get_question_type.short_description = 'Question Type'
    get_question_type.admin_order_field = 'question__question_type'

@admin.register(SurveyResponse)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('survey', 'created_at')
    list_filter = ['survey', 'created_at']
    readonly_fields = ['survey', 'created_at']
    inlines = [AnswerInline]

    def has_add_permission(self, request):
        return False  # 管理画面からの手動追加を防止