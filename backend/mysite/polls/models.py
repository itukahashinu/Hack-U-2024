from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name='Category name')
    description = models.TextField(blank=True, verbose_name='Category description')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'
        ordering = ['name']

class Survey(models.Model):
    STATUS_CHOICES = [
        ('draft', '下書き'),
        ('active', '進行中'),
        ('paused', '一時停止'),
        ('closed', '終了'),
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
        default='active',
        verbose_name='ステータス'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='surveys',
        verbose_name='Category'
    )
    image = models.ImageField(
        upload_to='survey_images/',
        null=True,
        blank=True,
        verbose_name='Survey image'
    )
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='surveys_created',
        verbose_name='Creator',
        null=True
    )
    @property
    def progress(self):
        if self.required_responses == 0:
            return 0
        return int((self.current_responses / self.required_responses) * 100)

    @property
    def days_left(self):
        if self.end_date < timezone.now():
            return 0
        return (self.end_date - timezone.now()).days

    @property
    def participants(self):
        return self.responses.count()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'survey'
        verbose_name_plural = 'surveys'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # 現在の日時
        now = timezone.now()
        
        # 新規作成時はステータスの自動設定を行わない
        if not self.pk:  # 新規作成時
            super().save(*args, **kwargs)
            return
            
        # 既存のアンケートの場合のみ、日時に基づいてステータスを自動更新
        if self.status == 'active':
            if now > self.end_date:
                self.status = 'closed'
        
        super().save(*args, **kwargs)

    def update_status(self):
        """
        現在の日時に基づいてステータスを更新する
        """
        now = timezone.now()
        if self.status != 'paused':  # 一時停止中は自動更新しない
            if now < self.start_date:
                self.status = 'draft'
            elif now > self.end_date:
                self.status = 'closed'
            elif self.start_date <= now <= self.end_date:
                self.status = 'active'
        self.save()

    def get_questions(self):
        """質問を順序付きで取得"""
        return self.questions.all().order_by('order')

    def has_questions(self):
        """質問が存在するかチェック"""
        return self.questions.exists()

    def get_question_count(self):
        """質問数を取得"""
        return self.questions.count()

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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def get_choices(self):
        """選択肢を順序付きで取得"""
        return self.choices.all().order_by('order')

    def has_choices(self):
        """選択肢が存在するかチェック"""
        return self.choices.exists()

    def get_choice_count(self):
        """選択肢数を取得"""
        return self.choices.count()

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

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)

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

@receiver(post_save, sender=Question)
def create_default_choices(sender, instance, created, **kwargs):
    """質問作成時にデフォルトの選択肢を作成"""
    # 選択肢が存在しない場合かつ管理画面からの作成時のみデフォルト選択肢を作成
    if created and not instance.choices.exists() and hasattr(instance, '_from_admin'):
        print(f"\nCreating default choices for question: {instance.question_text}")
        Choice.objects.create(
            question=instance,
            choice_text='選択肢 1',
            order=1
        )
        Choice.objects.create(
            question=instance,
            choice_text='選択肢 2',
            order=2
        )

################################################

class SurveyParticipant(models.Model):
    """
    サーベイ参加者の追跡モデル
    各サーベイに対するユーザーの参加状況を管理
    """
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name='participants_tracking',
        verbose_name='アンケート'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='participated_surveys',
        verbose_name='ユーザー'
    )
    choice_id = models.IntegerField(
        default=0,
        verbose_name='選択肢ID'
    )
    is_answered = models.BooleanField(
        default=False,
        verbose_name='回答済みフラグ'
    )
    participation_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='参加日時'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='作成日時'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新日時'
    )

    class Meta:
        unique_together = ('survey', 'user')
        verbose_name = '回答者'
        verbose_name_plural = '回答者一覧'
        indexes = [
            models.Index(fields=['user', 'is_answered']),
            models.Index(fields=['survey', 'is_answered'])
        ]

    def __str__(self):
        return f"{self.user.username} - {self.survey.title}"
