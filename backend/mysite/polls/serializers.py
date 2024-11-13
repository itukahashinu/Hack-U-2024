from rest_framework import serializers
from .models import Survey, Question, Choice, SurveyResponse, Answer

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'choice_text']

class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'question_text', 'question_type', 'is_required', 'choices']

class SurveySerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Survey
        fields = ['id', 'title', 'description', 'questions']

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['question', 'selected_choices']

class ResponseSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = SurveyResponse
        fields = ['survey', 'answers']

    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        response = Response.objects.create(**validated_data)
        
        for answer_data in answers_data:
            answer = Answer.objects.create(
                response=response,
                question=answer_data['question']
            )
            answer.selected_choices.set(answer_data['selected_choices'])
        
        return response