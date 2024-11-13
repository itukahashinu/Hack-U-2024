from django.db import models
from django.utils import timezone

class Survey(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('closed', 'Closed'),
    ]

    title = models.CharField(max_length=200, verbose_name='Title')
    description = models.TextField(verbose_name='Description', blank=True)
    created_at = models.DateTimeField('Creation date', auto_now_add=True)
    start_date = models.DateTimeField('Start date', default=timezone.now)
    end_date = models.DateTimeField('End date')
    required_responses = models.IntegerField(
        default=0, 
        verbose_name='Required responses'
    )
    current_responses = models.IntegerField(
        default=0,
        verbose_name='Current responses'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Status'
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'survey'
        verbose_name_plural = 'surveys'
        ordering = ['-created_at']

class Question(models.Model):
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='Survey'
    )
    question_text = models.CharField(
        max_length=200,
        verbose_name='Question text'
    )
    question_type = models.CharField(
        max_length=20,
        choices=[
            ('radio', 'Single choice (Radio)'),
            ('checkbox', 'Multiple choice (Checkbox)'),
        ],
        default='radio',
        verbose_name='Question type'
    )
    is_required = models.BooleanField(
        default=True,
        verbose_name='Required'
    )
    order = models.IntegerField(
        default=0,
        verbose_name='Display order'
    )

    def __str__(self):
        return self.question_text

    class Meta:
        verbose_name = 'question'
        verbose_name_plural = 'questions'
        ordering = ['survey', 'order']

class Choice(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='choices',
        verbose_name='Question'
    )
    choice_text = models.CharField(
        max_length=200,
        verbose_name='Choice text'
    )
    votes = models.IntegerField(
        default=0,
        verbose_name='Votes'
    )
    order = models.IntegerField(
        default=0,
        verbose_name='Display order'
    )

    def __str__(self):
        return self.choice_text

    class Meta:
        verbose_name = 'choice'
        verbose_name_plural = 'choices'
        ordering = ['question', 'order']

class SurveyResponse(models.Model):
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name='responses',
        verbose_name='Survey'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Response date'
    )

    def __str__(self):
        return f"Response to {self.survey.title} at {self.created_at}"

    class Meta:
        verbose_name = 'survey response'
        verbose_name_plural = 'survey responses'
        ordering = ['-created_at']

class Answer(models.Model):
    response = models.ForeignKey(
        SurveyResponse,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='Response'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='Question'
    )
    selected_choices = models.ManyToManyField(
        Choice,
        related_name='answers',
        verbose_name='Selected choices'
    )

    def __str__(self):
        return f"Answer to {self.question.question_text}"

    class Meta:
        verbose_name = 'answer'
        verbose_name_plural = 'answers'