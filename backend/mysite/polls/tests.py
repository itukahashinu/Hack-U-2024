from django.test import TestCase
from django.contrib.auth.models import User
from .models import Survey, SurveyParticipant

class SurveyParticipantModelTest(TestCase):

    def setUp(self):
        # テスト用のユーザーとサーベイを作成
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.survey = Survey.objects.create(title='Test Survey')

    def test_participant_creation(self):
        # サーベイ参加者を作成
        participant = SurveyParticipant.objects.create(survey=self.survey, user=self.user)
        
        # 参加者が正しく作成されたか確認
        self.assertEqual(participant.survey, self.survey)
        self.assertEqual(participant.user, self.user)
        self.assertFalse(participant.is_answered)

    def test_mark_as_completed(self):
        # 参加者を作成
        participant = SurveyParticipant.objects.create(survey=self.survey, user=self.user)
        
        # 完了処理を実行
        participant.mark_as_completed()
        
        # 完了フラグがTrueになっているか確認
        self.assertTrue(participant.is_answered)