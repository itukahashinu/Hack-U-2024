from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import get_object_or_404, render
from .models import Question, Choice , Survey
from django.http import Http404
from rest_framework import viewsets, status
from rest_framework.decorators import api_view,action,permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import SurveySerializer , QuestionSerializer
import requests
import datetime

def create_google_form_mock(survey_data):
    """
    Google Forms APIのモック関数
    """
    # 既存のデバッグ出力を強化
    print("\n=== Google Form Creation Debug Log ===")
    print("Timestamp:", datetime.datetime.now())
    print("\nReceived Survey Data:")
    print(f"Title: {survey_data.get('title', 'Untitled Survey')}")
    print(f"Description: {survey_data.get('description', '')}")
    
    # 質問データの詳細なログ
    if 'questions' in survey_data:
        print("\nQuestions Details:")
        for i, question in enumerate(survey_data['questions'], 1):
            print(f"\nQuestion {i}:")
            print(f"Text: {question.get('question_text', '')}")
            print(f"Type: {question.get('question_type', '')}")
            if 'choices' in question:
                print("Choices:", [choice.get('choice_text', '') for choice in question['choices']])

    mock_form_id = f"mock_form_{hash(str(survey_data))}"
    print(f"\nGenerated Form ID: {mock_form_id}")
    print("=== End of Debug Log ===\n")
    
    return mock_form_id

def index(request):
    # Surveyモデルから全てのデータを取得（最新順）
    surveys = Survey.objects.prefetch_related('questions__choices').order_by('-created_at')
    
    # デバッグ情報
    print("\n=== Debug Information ===")
    for survey in surveys:
        print(f"\nSurvey ID: {survey.id}")
        print(f"Title: {survey.title}")
        print(f"Description: {survey.description}")
        for question in survey.questions.all():
            print(f"- Question: {question.question_text}")
            print(f"  Choices: {[c.choice_text for c in question.choices.all()]}")

    return render(request, 'polls/index.html', {
        'surveys': surveys,
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
@permission_classes([AllowAny])
def create_survey(request):
    # POSTメソッド以外の場合のエラーメッセージを追加
    if request.method != 'POST':
        return Response(
            {"error": "GET method is not allowed for this endpoint. Please use POST."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    # POSTメソッドの場合の処理
    serializer = SurveySerializer(data=request.data)
    
    if serializer.is_valid():
        # バリデーションが成功した場合、Google Formを作成（モック）
        survey_data = serializer.validated_data

        # 以下は既存の質問データの構成整形などの処理
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
    permission_classes = [AllowAny]

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

@api_view(['GET'])
@permission_classes([AllowAny])  # この行を追加
def debug_forms(request):
    """デバッグ用：作成されたすべてのフォームを表示"""
    try:
        surveys = Survey.objects.all()
        debug_info = []
        
        for survey in surveys:
            form_info = {
                'id': survey.id,
                'title': survey.title,
                'description': survey.description,
                'google_form_id': survey.google_form_id,
                'created_at': survey.created_at,
                'status': survey.status,
                'questions': []
            }
            
            # 質問と選択肢の情報を追加
            for question in survey.questions.all():
                question_info = {
                    'text': question.question_text,
                    'type': question.question_type,
                    'choices': []
                }
                
                # 選択肢がある場合のみ追加
                if question.question_type in ['single_choice', 'multiple_choice']:
                    question_info['choices'] = [
                        {
                            'text': choice.choice_text,
                            'votes': choice.votes
                        } for choice in question.choices.all()
                    ]
                
                form_info['questions'].append(question_info)
            
            debug_info.append(form_info)
        
        return Response({
            'total_forms': len(debug_info),
            'forms': debug_info,
            'timestamp': datetime.datetime.now()
        })
        
    except Exception as e:
        return Response({
            'error': str(e),
            'timestamp': datetime.datetime.now()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ... existing code ...

@api_view(['GET'])
@permission_classes([AllowAny])
def survey_list(request):
    """アンケート一覧を取得するAPI"""
    try:
        surveys = Survey.objects.prefetch_related('questions').all()
        surveys_data = []
        
        for survey in surveys:
            survey_info = {
                'id': survey.id,
                'title': survey.title,
                'description': survey.description,
                'questions_count': survey.questions.count(),
                'required_responses': survey.required_responses,
                'current_responses': survey.current_responses,
                'deadline': survey.deadline,
                'status': survey.status,
                'created_at': survey.created_at,
                'is_entrance_survey': survey.is_entrance_survey,
                # フロントエンド用のURLを追加
                'detail_url': f'/surveys/{survey.id}/',  # フロントエンドのルート
                # バックエンドAPIのURLを追加
                'api_url': f'/api/surveys/{survey.id}/'
            }
            surveys_data.append(survey_info)
        
        return Response({
            'surveys': surveys_data
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def survey_detail(request, survey_id):
    """個別のアンケート詳細を取得するAPI"""
    try:
        survey = Survey.objects.prefetch_related('questions__choices').get(pk=survey_id)
        
        questions_data = []
        for question in survey.questions.all():
            question_data = {
                'id': question.id,
                'question_text': question.question_text,
                'question_type': question.question_type,
                'choices': []
            }
            
            if question.question_type in ['single_choice', 'multiple_choice']:
                question_data['choices'] = [{
                    'id': choice.id,
                    'choice_text': choice.choice_text,
                    'votes': choice.votes
                } for choice in question.choices.all()]
            
            questions_data.append(question_data)
        
        survey_data = {
            'id': survey.id,
            'title': survey.title,
            'description': survey.description,
            'required_responses': survey.required_responses,
            'current_responses': survey.current_responses,
            'deadline': survey.deadline,
            'status': survey.status,
            'created_at': survey.created_at,
            'is_entrance_survey': survey.is_entrance_survey,
            'questions': questions_data
        }
        
        return Response(survey_data)
        
    except Survey.DoesNotExist:
        return Response({
            'error': 'Survey not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def survey_detail_view(request, survey_id):
    """アンケート詳細を表示するビュー"""
    try:
        survey = Survey.objects.prefetch_related('questions__choices').get(pk=survey_id)
        return render(request, 'polls/survey_detail.html', {
            'survey': survey
        })
    except Survey.DoesNotExist:
        raise Http404("アンケートが見つかりません")