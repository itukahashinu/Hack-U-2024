from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import get_object_or_404, render
from .models import Question, Choice , Survey
from django.http import Http404
from rest_framework import viewsets, status
from rest_framework.decorators import api_view,action
from rest_framework.response import Response
from .serializers import SurveySerializer , QuestionSerializer
import requests
"""
# Google Forms APIのモック関数
def create_google_form_mock(survey_data):
    
    Google Forms APIのリクエストをモックする関数
    実際のGoogle Forms APIのリクエストは行わず、仮のIDを返す
    
    # モックデータとして、成功したフォームIDを返す
    print("Mocked create_google_form called with survey data:", survey_data)
    
    # モックされたフォームID
    return "mock_form_id_12345"

##########################
"""
def index(request):
    latest_question_list = Question.objects.order_by('-created_at')[:5]
    return render(request, 'polls/index.html', {
        'latest_question_list': latest_question_list,
    })

def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    # デバッグ情報を追加
    print(f"Question ID: {question.id}")
    print(f"Question Text: {question.question_text}")
    print(f"Choices count: {question.choices.count()}")
    print(f"Choices: {list(question.choices.all())}")
    
    return render(request, "polls/detail.html", {
        "question": question,
    })

def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    total_votes = sum(choice.votes for choice in question.choices.all())
    
    # デバッグ情報を追加
    print(f"Question ID: {question.id}")
    print(f"Question Text: {question.question_text}")
    print(f"Total votes: {total_votes}")
    print(f"Choices and votes:")
    for choice in question.choices.all():
        print(f"- {choice.choice_text}: {choice.votes} votes")
    
    return render(request, "polls/results.html", {
        "question": question,
        "total_votes": total_votes
    })

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choices.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # 選択肢が選ばれていない場合のエラー処理
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "選択肢を選んでください。",
        })
    else:
        # 投票数を増やして保存
        selected_choice.votes += 1
        selected_choice.save()
        # デバッグ情報
        print(f"Vote recorded for {selected_choice.choice_text}")
        print(f"New vote count: {selected_choice.votes}")
        
        # POST-Redirect-GETパターンに従ってリダイレクト
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))




###########################
# Google Forms APIへのリクエストをモックした処理
@api_view(['POST'])
def create_survey(request):
    """
    アンケート作成用APIエンドポイント
    フロントエンドから送られたアンケートデータを受け取り、モックされたGoogle Forms APIでフォームを作成
    """
    if request.method == 'POST':
        serializer = SurveySerializer(data=request.data)
        
        if serializer.is_valid():
            # バリデーションが成功した場合、Google Formを作成（モック）
            survey_data = serializer.validated_data

            # 質問データの構成を整える
            questions_data = []
            for question in survey_data['questions']:
                if question['question_type'] in ['single_choice', 'multiple_choice']:
                    choices = question['choices']
                    question_data = {
                        'question_text': question['question_text'],
                        'question_type': question['question_type'],
                        'choices': [{"choice_text": choice} for choice in choices],
                    }
                else:
                    question_data = {
                        'question_text': question['question_text'],
                        'question_type': question['question_type'],
                    }
                questions_data.append(question_data)

            survey_data['questions'] = questions_data

            # Google Formをモックして作成
            google_form_id = create_google_form_mock(survey_data)
            
            if google_form_id:
                return Response({
                    'message': 'Survey created successfully!',
                    'google_form_id': google_form_id,  # モックされたGoogle FormのID
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'message': 'Failed to create the survey form.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            # バリデーションエラーが発生した場合
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def question_detail(request, question_id):
    try:
        question = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        return Response({'error': 'Question not found'}, status=404)

    serializer = QuestionSerializer(question)
    return Response(serializer.data)

class SurveyViewSet(viewsets.ModelViewSet):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer

    @action(detail=True, methods=['post'])
    def create_google_form(self, request, pk=None):
        """Google Formを作成するアクション"""
        survey = self.get_object()
        try:
            # Google Form APIのモック関数を呼び出し
            form_id = create_google_form_mock(survey)
            survey.google_form_id = form_id
            survey.save()
            return Response({
                'message': 'Google Form created successfully',
                'form_id': form_id
            })
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def submit_response(self, request, pk=None):
        """アンケート回答を送信するアクション"""
        survey = self.get_object()
        try:
            # 回答データを処理
            survey.current_responses += 1
            survey.save()
            return Response({
                'message': 'Response submitted successfully'
            })
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def get_entrance_survey(self, request):
        """入口アンケートをランダムに取得するアクション"""
        try:
            # ランダムな入口アンケートを取得
            entrance_survey = Survey.objects.filter(
                is_entrance_survey=True,
                status='active'
            ).order_by('?').first()
            
            if not entrance_survey:
                return Response({
                    'message': 'No entrance surveys available'
                }, status=status.HTTP_404_NOT_FOUND)
                
            serializer = self.get_serializer(entrance_survey)
            return Response(serializer.data)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def get_results(self, request, pk=None):
        """アンケート結果を取得するアクション"""
        survey = self.get_object()
        try:
            # 結果データを取得（ここではモックデータを返す）
            results = {
                'total_responses': survey.current_responses,
                'questions': []
            }
            
            for question in survey.questions.all():
                question_data = {
                    'question_text': question.question_text,
                    'choices': [{
                        'choice_text': choice.choice_text,
                        'votes': choice.votes
                    } for choice in question.choices.all()]
                }
                results['questions'].append(question_data)
                
            return Response(results)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)