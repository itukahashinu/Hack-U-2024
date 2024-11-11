from rest_framework import serializers
from .models import Survey, Question, Choice

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'choice_text', 'votes']

class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'question_text', 'question_type', 'choices', 'created_at']

class SurveySerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Survey
        fields = [
            'id',
            'title',
            'description',
            'google_form_id',
            'spreadsheet_id',
            'is_entrance_survey',
            'required_responses',
            'current_responses',
            'status',
            'created_at',
            'questions'
        ]