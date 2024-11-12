from django.db import models
from django.utils import timezone

class Survey(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    google_form_id = models.CharField(max_length=200, blank=True)
    spreadsheet_id = models.CharField(max_length=200, blank=True)
    is_entrance_survey = models.BooleanField(default=False)
    required_responses = models.IntegerField(default=0)
    current_responses = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', '下書き'),
            ('active', '実施中'),
            ('completed', '完了')
        ],
        default='draft'
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']

class Question(models.Model):
    QUESTION_TYPES = [
        ('single_choice', 'Single Choice'),
        ('multiple_choice', 'Multiple Choice'),
        ('text', 'Text Answer'),
    ]
    
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
    question_text = models.CharField(max_length=200)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question_text
    
    def get_choices(self):
        return self.choices.all()

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text