from django.contrib import admin
from django.db import models
from .models import Survey, Question, Choice, Category, SurveyResponse, Answer

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2
    min_num = 2
    validate_min = True
    fields = ['choice_text', 'order']
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if obj:
            formset.form.base_fields['choice_text'].initial = ''
        return formset

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    min_num = 1
    validate_min = True
    fields = ['question_text', 'question_type', 'is_required', 'order']
    show_change_link = True

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        print(f"Question formset for survey: {obj}")
        return formset

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

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'survey', 'question_type', 'is_required', 'order')
    list_filter = ['survey', 'question_type', 'is_required']
    search_fields = ['question_text', 'survey__title']
    fields = ['survey', 'question_text', 'question_type', 'is_required', 'order']
    inlines = [ChoiceInline]

    def save_model(self, request, obj, form, change):
        """質問保存時の処理"""
        if not change:
            obj._from_admin = True
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        """選択肢の保存時の処理"""
        if formset.model != Choice:
            return super().save_formset(request, form, formset, change)

        print(f"Saving choices for question: {form.instance.question_text}")
        
        if not formset.is_valid():
            return
            
        instances = formset.save(commit=False)
        
        # 既存の選択肢を処理
        if change:
            formset.save_existing_objects()
            formset.delete_objects()
        
        # 新しい選択肢を保存
        for instance in instances:
            if not instance.order:
                max_order = Choice.objects.filter(
                    question=instance.question
                ).aggregate(models.Max('order'))['order__max'] or 0
                instance.order = max_order + 1
            print(f"Saving choice: {instance.choice_text} with order {instance.order}")
            instance.save()
        
        formset.save_m2m()

@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('choice_text', 'question', 'order')
    list_filter = ['question__survey']
    search_fields = ['choice_text', 'question__question_text']
    fields = ['question', 'choice_text', 'order']

# 残りのモデルを登録
admin.site.register(Category)
admin.site.register(SurveyResponse)
admin.site.register(Answer)