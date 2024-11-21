from django.contrib import admin
from .models import Survey, Question, Choice, SurveyResponse, Answer

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2  # 最低2つの選択肢を表示
    min_num = 2  # 最低2つの選択肢を必須に
    validate_min = True  # 最低数のバリデーションを有効化
    fields = ['choice_text', 'order']

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    min_num = 1  # 最低1つの質問を必須に
    validate_min = True  # 最低数のバリデーションを有効化
    fields = ['question_text', 'question_type', 'is_required', 'order']
    show_change_link = True
    inlines = [ChoiceInline]  # 質問内に選択肢を表示

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
        (None, {'fields': ['title', 'description', 'image', 'category']}),
        ('Schedule', {
            'fields': ['start_date', 'end_date', 'required_responses'],
            'description': 'アンケートのスケジュールと必要回答数を設定してください'
        }),
        ('Status', {
            'fields': ['status'],
            'description': 'ステータスは日付に基づいて自動的に更新されます'
        }),
    ]
    inlines = [QuestionInline]

    def save_formset(self, request, form, formset, change):
        """質問と選択肢の保存時の追加処理"""
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, Question):
                if not instance.order:  # orderが設定されていない場合
                    # 既存の質問数を取得して順番を設定
                    max_order = Question.objects.filter(
                        survey=instance.survey
                    ).aggregate(models.Max('order'))['order__max'] or 0
                    instance.order = max_order + 1
            elif isinstance(instance, Choice):
                if not instance.order:  # orderが設定されていない場合
                    # 既存の選択肢数を取得して順番を設定
                    max_order = Choice.objects.filter(
                        question=instance.question
                    ).aggregate(models.Max('order'))['order__max'] or 0
                    instance.order = max_order + 1
            instance.save()
        formset.save_m2m()

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'survey', 'question_type', 'is_required', 'order')
    list_filter = ['survey', 'question_type', 'is_required']
    search_fields = ['question_text', 'survey__title']
    fields = ['survey', 'question_text', 'question_type', 'is_required', 'order']
    inlines = [ChoiceInline]


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

# admin.site.register(SurveyResponse) の代わりに
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('survey', 'created_at')
    list_filter = ['survey', 'created_at']
    readonly_fields = ['survey', 'created_at']
    inlines = [AnswerInline]

    def has_add_permission(self, request):
        return False  # 管理画面からの手動追加を防止

    class Meta:
        managed = True
        verbose_name = 'survey response'
        verbose_name_plural = 'survey responses'

# 管理画面に表示せずにモデルを登録
admin.site.register(SurveyResponse, ResponseAdmin)
admin.site.unregister(SurveyResponse)  # 管理画面から非表示にする