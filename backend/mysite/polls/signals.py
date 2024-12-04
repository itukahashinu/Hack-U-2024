from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Survey, SurveyParticipant

@receiver(post_save, sender=Survey)
def create_survey_participants(sender, instance, created, **kwargs):
    """
    新しいサーベイ作成時に全ユーザーの参加者エントリーを自動作成
    """
    if created:
        users = User.objects.all()
        for user in users:
            SurveyParticipant.objects.create(
                survey=instance,
                user=user,
                is_answered=False
            )