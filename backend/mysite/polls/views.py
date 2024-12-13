from django.http import HttpResponseRedirect, Http404, JsonResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404, render, redirect
from django.db import transaction, models
from django.db.models import F
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response as DRFResponse #DjangoFrameworkResponse
from rest_framework.permissions import AllowAny
from .models import (
    Question,
    Choice,
    Survey,
    SurveyResponse,
    Answer,
    Category,
    SurveyParticipant
)
from .serializers import SurveySerializer, QuestionSerializer
import requests, datetime, json
import traceback
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import re
from django.db.models import Q
from django.core.exceptions import PermissionDenied

def create_google_form_mock(survey_data):
    """
    Google Forms APIのモック関数
    """
    # 既存のバッグ出力を強化
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
    # パラメーターの取得
    search_query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    sort_by = request.GET.get('sort', '-start_date')  # ソート条件の取得
    
    # Surveyモデルから全てのデータを取得（sort_byで指定した順）
    if sort_by == "-start_date" or sort_by == "-current_responses":
        surveys = Survey.objects.prefetch_related('questions__choices').order_by(sort_by)
    elif sort_by == "-end_date":
        surveys = Survey.objects.prefetch_related('questions__choices').order_by(sort_by).reverse()
    
    # デバッグ情報
    print("\n=== Debug Information ===")
    for survey in surveys:
        print(f"\nSurvey: {survey.title}")
        print(f"Creator: {survey.creator}")
        print(f"Current User: {request.user}")
        print(f"Is Creator: {survey.creator == request.user}")
    
    if sort_by == "-start_date" or sort_by == "-current_responses":
        surveys = Survey.objects.prefetch_related(
            'questions__choices',
            'responses__answers__selected_choices'
        ).order_by(sort_by)
    elif sort_by == "-end_date":
        surveys = Survey.objects.prefetch_related(
            'questions__choices',
            'responses__answers__selected_choices'
        ).order_by(sort_by).reverse()
    
    # 検索クエリがある場合、フィルタリング
    if search_query:
        surveys = surveys.filter(
            Q(title__icontains=search_query) |          # タイトル
            Q(description__icontains=search_query) |    # 説明文
            Q(category__name__icontains=search_query)   # カテゴリー名
        ).distinct()
    
    # カテゴリーでフィルタリング
    if category_id and category_id != 'all':
        surveys = surveys.filter(category_id=category_id)
    
    return render(request, 'polls/index.html', {
        'surveys': surveys,
        'categories': Category.objects.all(),
        'search_query': search_query,
        'selected_category': category_id,
        'sort_by': sort_by,
        'debug': settings.DEBUG,
        'user': request.user,
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

@login_required
def create_survey(request):
    if request.method == 'POST':
        print("\n=== Survey Creation Debug ===")
        print("POST data:", request.POST)
        
        try:
            with transaction.atomic():
                # アンケートの基本情報を保存
                survey = Survey.objects.create(
                    title=request.POST['title'],
                    description=request.POST.get('description', ''),
                    start_date=request.POST['start_date'],
                    end_date=request.POST['end_date'],
                    required_responses=request.POST.get('required_responses', 0),
                    status=request.POST['status'],
                    category_id=request.POST.get('category'),
                    creator=request.user
                )

                # 質問の処理
                questions_data = {}
                for key, value in request.POST.items():
                    if key.startswith('questions[') and '[text]' in key:
                        match = re.match(r'questions\[(\d+)\]\[text\]', key)
                        if match:
                            index = match.group(1)
                            questions_data[index] = {
                                'text': value,
                                'type': request.POST.get(f'questions[{index}][type]', 'radio'),
                                'required': request.POST.get(f'questions[{index}][required]') == 'on',
                                'choices': request.POST.getlist(f'questions[{index}][choices][]')
                            }

                print("Processed questions data:", questions_data)

                # 質問と選択肢を保存
                for index, q_data in questions_data.items():
                    if q_data['text'].strip():
                        question = Question.objects.create(
                            survey=survey,
                            question_text=q_data['text'],
                            question_type=q_data['type'],
                            is_required=q_data['required'],
                            order=int(index) + 1
                        )
                        
                        # 選択肢を保存
                        for i, choice_text in enumerate(q_data['choices'], 1):
                            if choice_text.strip():
                                Choice.objects.create(
                                    question=question,
                                    choice_text=choice_text,
                                    order=i
                                )
                                print(f"Created choice: {choice_text}")

                messages.success(request, 'アンケートが作成されました。')
                return redirect('polls:index')  # インデックスページにリダイレクト

        except Exception as e:
            print(f"Error creating survey: {e}")
            print(traceback.format_exc())  # 詳細なエラー情報を出力
            messages.error(request, f'アンケートの作成中にエラーが発生しました: {str(e)}')
            return render(request, 'polls/survey_create.html', {
                'categories': Category.objects.all(),
                'error': str(e)
            })

    # GETリクエストの場合
    return render(request, 'polls/survey_create.html', {
        'categories': Category.objects.all()
    })


@api_view(['GET'])
def question_detail(request, question_id):
    try:
        question = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        return DRFResponse({'error': 'Question not found'}, status=404)

    serializer = QuestionSerializer(question)
    return DRFResponse(serializer.data)

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
            return DRFResponse({
                'message': 'Google Form created successfully',
                'form_id': form_id
            })
        except Exception as e:
            return DRFResponse({
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
            return DRFResponse({
                'message': 'Response submitted successfully'
            })
        except Exception as e:
            return DRFResponse({
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
                return DRFResponse({
                    'message': 'No entrance surveys available'
                }, status=status.HTTP_404_NOT_FOUND)
                
            serializer = self.get_serializer(entrance_survey)
            return DRFResponse(serializer.data)
        except Exception as e:
            return DRFResponse({
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
                
            return DRFResponse(results)
        except Exception as e:
            return DRFResponse({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])  # この行追加
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
        
        return DRFResponse({
            'total_forms': len(debug_info),
            'forms': debug_info,
            'timestamp': datetime.datetime.now()
        })
        
    except Exception as e:
        return DRFResponse({
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
        
        return DRFResponse({
            'surveys': surveys_data
        })
        
    except Exception as e:
        return DRFResponse({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def survey_detail_view(request, survey_id):
    survey = get_object_or_404(
        Survey.objects.prefetch_related('questions__choices'),
        pk=survey_id
    )
    
    # 自分が参加者かどうかをチェック
    is_participant = SurveyParticipant.objects.filter(
        survey=survey,
        user=request.user
    ).exists()

    context = {
        'survey': survey,
        'questions': survey.questions.all().order_by('order'),  # 順序で並び替え
        'can_respond': survey.status == 'active' and not is_participant,
        'debug': settings.DEBUG  # デバッグ情報の表示用
    }
    
    return render(request, 'polls/survey_detail.html', context)

@api_view(['GET'])
@permission_classes([AllowAny])
def survey_detail(request, survey_id):
    """アンケートの詳細を表示するビュー"""
    # prefetch_relatedを使用して関連データを効率的に取得
    survey = get_object_or_404(
        Survey.objects.prefetch_related(
            'questions__choices'  # 質問と選択肢を一度に取得
        ),
        id=survey_id
    )
    
    # デバッグ情報
    print("\n=== Survey Detail Debug ===")
    print(f"Survey: {survey.title}")
    print(f"Questions count: {survey.questions.count()}")
    for question in survey.questions.all().order_by('order'):
        print(f"\nQuestion: {question.question_text}")
        print(f"Question Type: {question.question_type}")
        print(f"Choices count: {question.choices.count()}")
        for choice in question.choices.all().order_by('order'):
            print(f"- Choice: {choice.choice_text}")
    
    context = {
        'survey': survey,
        'questions': survey.questions.all().order_by('order'),  # 質問を順序で並び替え
        'debug': settings.DEBUG
    }
    
    return render(request, 'polls/survey_detail.html', context)

def survey_response_view(request, survey_id):
    survey = get_object_or_404(
        Survey.objects.prefetch_related('questions__choices'),
        pk=survey_id
    )
    
    # デバッグ情報をコンソールに出力
    if settings.DEBUG:
        print("\n=== Survey Response Debug Information ===")
        print(f"Survey ID: {survey.id}")
        print(f"Request method: {request.method}")
        if request.method == 'POST':
            print("\nPOST data:")
            for key, value in request.POST.items():
                print(f"- {key}: {value}")
    
    # GETリクエストまたはエラー時の処理
    context = {
        'survey': survey,
        'questions_json': json.dumps([{
            'id': q.id,
            'text': q.question_text,
            'type': q.question_type,
            'is_required': q.is_required,
            'choices': [{
                'id': c.id,
                'text': c.choice_text
            } for c in q.choices.all()]
        } for q in survey.questions.all()]),
        'debug': settings.DEBUG
    }
    
    return render(request, 'polls/survey_response.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def submit_survey_response(request, survey_id):
    """アンケート回答を送信するAPI"""
    try:
        with transaction.atomic():
            # リクエストボディをJSONとしてパース
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({
                    'error': '無効なJSONフォーマットです。'
                }, status=400)

            # デバッグ出力
            print(f"Received response data for survey {survey_id}:")
            print(json.dumps(data, indent=2, ensure_ascii=False))

            # アンケートの取得
            survey = get_object_or_404(Survey, pk=survey_id)
            
            # アンケートのステータスチェック
            if survey.status != 'active':
                return JsonResponse({
                    'error': 'このアンケートは現在回答を受け付けていません。'
                }, status=400)

            # 回答データの検証
            answers = data.get('answers', [])
            if not answers:
                return JsonResponse({
                    'error': '回答が選択されていません。'
                }, status=400)

            # 必須回答のチェック
            required_questions = survey.questions.filter(is_required=True).values_list('id', flat=True)
            answered_questions = {answer['question_id'] for answer in answers}
            missing_required = set(required_questions) - answered_questions
            
            if missing_required:
                return JsonResponse({
                    'error': '必須の質問に回答してください。',
                    'missing_questions': list(missing_required)
                }, status=400)

            # 回答を保存
            response = SurveyResponse.objects.create(survey=survey)
            
            for answer_data in answers:
                question_id = answer_data['question_id']
                choice_ids = answer_data.get('choice_ids', [])
                
                question = survey.questions.get(id=question_id)
                answer = Answer.objects.create(
                    response=response,
                    question=question
                )
                
                # 選択肢の保存と投票数の更新
                for choice_id in choice_ids:
                    choice = Choice.objects.select_for_update().get(
                        id=choice_id,
                        question=question
                    )
                    choice.votes = F('votes') + 1
                    choice.save()
                    answer.selected_choices.add(choice)

            # 回答数を更新
            survey.current_responses = F('current_responses') + 1
            survey.save()

            # 必要回答数に達したかチェック
            survey.refresh_from_db()
            if survey.current_responses >= survey.required_responses:
                survey.status = 'closed'
                survey.save()

            return JsonResponse({
                'message': '回答を受け付けました。ご協力ありがとうございます。',
                'response_id': response.id
            })

    except Exception as e:
        print(f"Error processing survey response: {str(e)}")
        return JsonResponse({
            'error': '回答の処理中にエラーが発生しました。'
        }, status=500)

@login_required
def survey_create_view(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # アンケートの基本情報を保存
                survey = Survey.objects.create(
                    title=request.POST['title'],
                    description=request.POST['description'],
                    start_date=request.POST['start_date'],
                    end_date=request.POST['end_date'],
                    required_responses=int(request.POST['required_responses']),
                    status='active'
                )

                # 質問と選択肢を保存
                questions_data = parse_questions_data(request.POST)
                for q_data in questions_data:
                    question = Question.objects.create(
                        survey=survey,
                        question_text=q_data['text'],
                        question_type=q_data['type'],
                        is_required=q_data['required'],
                        order=q_data['order']
                    )
                    
                    # 選択肢を保存
                    for i, choice_text in enumerate(q_data['choices']):
                        Choice.objects.create(
                            question=question,
                            choice_text=choice_text,
                            order=i
                        )

                messages.success(request, 'アンケートが作成されました。')
                return redirect('polls:survey_detail', survey_id=survey.id)

        except Exception as e:
            messages.error(request, f'アンケートの作成中にエラーが発生しました: {str(e)}')
            return redirect('polls:survey_create')

    return render(request, 'polls/survey_create.html', {
        'now': timezone.now().strftime('%Y-%m-%dT%H:%M'),
        'min_date': timezone.now().strftime('%Y-%m-%dT%H:%M'),
    })

def parse_questions_data(post_data):
    """POSTデータから質問データを解析する"""
    questions = []
    current_question = None
    
    for key, value in post_data.items():
        if key.startswith('questions['):
            match = re.match(r'questions\[(\d+)\]\[(\w+)\](?:\[(\d+)\])?', key)
            if match:
                q_index, field, choice_index = match.groups()
                q_index = int(q_index)
                
                # 新しい質問の開始
                while len(questions) <= q_index:
                    questions.append({
                        'text': '',
                        'type': 'radio',
                        'required': False,
                        'choices': [],
                        'order': len(questions)
                    })
                
                if field == 'text':
                    questions[q_index]['text'] = value
                elif field == 'type':
                    questions[q_index]['type'] = value
                elif field == 'required':
                    questions[q_index]['required'] = value == 'on'
                elif field == 'choices' and choice_index:
                    questions[q_index]['choices'].append(value)
    
    return questions

@require_POST
def update_survey_status(request, survey_id):
    try:
        survey = Survey.objects.get(id=survey_id, author=request.user)
        new_status = request.POST.get('status')
        if new_status in dict(Survey.STATUS_CHOICES):
            survey.status = new_status
            survey.save()
            return JsonResponse({
                'status': 'success',
                'new_status': survey.get_status_display()
            })
    except Survey.DoesNotExist:
        return JsonResponse({'status': 'error'}, status=404)
    return JsonResponse({'status': 'error'}, status=400)

def survey_create(request):
    if request.method == 'POST':
        # デバッグ出力を追加
        print("POST data:", request.POST)
        print("Files:", request.FILES)
        
        # POSTデータから質問と選択肢を取得
        questions_data = {}
        for key, value in request.POST.items():
            if key.startswith('questions['):
                match = re.match(r'questions\[(\d+)\]\[(\w+)\]', key)
                if match:
                    q_index, q_field = match.groups()
                    if q_index not in questions_data:
                        questions_data[q_index] = {}
                    questions_data[q_index][q_field] = value
        
        print("Processed questions data:", questions_data)
        
        # アンケートの作成
        survey = Survey.objects.create(
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            author=request.user,
            start_date=request.POST.get('start_date'),
            end_date=request.POST.get('end_date'),
            required_responses=request.POST.get('required_responses', 0),
            status=request.POST.get('status', 'active')
        )

        # POSTデータから質問と選択肢を取得
        questions = []
        choices = {}
        
        for key, value in request.POST.items():
            # 質問のテキストを取得
            if key.startswith('questions[') and key.endswith('[text]'):
                index = key[key.find('[')+1:key.find(']')]
                questions.append({
                    'index': index,
                    'text': value,
                    'type': request.POST.get(f'questions[{index}][type]', 'radio')
                })
            
            # 選択肢を取得
            if key.startswith('questions[') and '[choices][]' in key:
                index = key[key.find('[')+1:key.find(']')]
                if index not in choices:
                    choices[index] = []
                if value.strip():  # 空の選択肢を除外
                    choices[index].append(value)

        # デバッグ用
        print("Questions:", questions)
        print("Choices:", choices)

        # 質問と選択肢を保存
        for q in questions:
            if q['text'].strip():  # 空の質問を除外
                question = Question.objects.create(
                    survey=survey,
                    question_text=q['text'],
                    question_type=q['type'],
                    is_required=True
                )
                
                #    の質問の選択肢を保存
                q_choices = choices.get(q['index'], [])
                for choice_text in q_choices:
                    Choice.objects.create(
                        question=question,
                        choice_text=choice_text
                    )
                
                # デバッグ用
                print(f"Created question: {question.question_text}")
                print(f"Created choices: {q_choices}")

        return redirect('polls:survey_detail', survey_id=survey.id)
    
    # GETリクエストの場合
    return render(request, 'polls/survey_create.html', {
        'categories': Category.objects.all()
    })

@login_required
def submit_survey(request, survey_id):
    if request.method != 'POST':
        return redirect('polls:survey_detail', survey_id=survey_id)
    
    survey = get_object_or_404(Survey, id=survey_id)
    
    # アンケートが回答可能な状態かチェック
    if survey.status != 'active':
        messages.error(request, 'このアンケートは現在回答を受け付けていません。')
        return redirect('polls:survey_detail', survey_id=survey_id)
    
    try:
        with transaction.atomic():
            # 回答レコードを作成
            response = SurveyResponse.objects.create(
                survey=survey
            )
            
            # 各質問への回答を保存
            for question in survey.questions.all():
                # 質問の回答を取得
                answer_key = f'question_{question.id}'
                if question.question_type == 'checkbox':
                    answer_key += '[]'
                    choice_ids = request.POST.getlist(answer_key)
                else:
                    choice_ids = [request.POST.get(answer_key)]
                
                # 必須チェック
                if question.is_required and not choice_ids:
                    raise ValueError(f'質問「{question.question_text}」は必須です。')
                
                # 回答を保存
                if choice_ids:
                    answer = Answer.objects.create(
                        response=response,
                        question=question
                    )
                    # 選択された選択肢を関連付け
                    selected_choices = Choice.objects.filter(id__in=choice_ids)
                    answer.selected_choices.set(selected_choices)
            
            # 回答数を更新
            survey.current_responses = F('current_responses') + 1
            survey.save()
            
            messages.success(request, 'アンケートの回答を送信しました。ご協力ありがとうございます。')
            return redirect('polls:index')
            
    except ValueError as e:
        messages.error(request, str(e))
    except Exception as e:
        messages.error(request, 'エラーが発生しました。もう一度お試しください。')
        print(f"Error submitting survey: {e}")
    
    return redirect('polls:survey_detail', survey_id=survey_id)

##########################################

def submit_survey_response(request, survey_id):
    try:
        with transaction.atomic():
            # サーベイ回答の処理
            
            # 参加者の状態を更新
            SurveyParticipant.objects.filter(
                survey_id=survey_id,
                user=request.user
            ).update(
                is_answered=True,
                participation_date=timezone.now()
            )
    except Exception as e:
        # エラーハンドリング
        pass

def unanswered_surveys(request):
    # 現在のユーザーが未回答の進行中のアンケートを取得
    unanswered_surveys = Survey.objects.filter(
        id__in=SurveyParticipant.objects.filter(
            user=request.user,
            is_answered=False
        ).values_list('survey_id', flat=True),
        status='active'  # ステータスが進行中のアンケート
    ).distinct()  # 重複を排除

    return render(request, 'polls/unanswered_surveys.html', {
        'unanswered_surveys': unanswered_surveys
    })

def get_active_surveys(request):
    # 現在のユーザーが未回答かつ回答可能なアンケートを取得
    unanswered_surveys = Survey.objects.filter(
        participants_tracking__user=request.user,
        participants_tracking__is_answered=False,
        status='active'  # ステータスが進行中のアンケート
    ).distinct()

    # アンケートの情報をJSON形式で返す
    surveys_data = [{
        'id': survey.id,
        'title': survey.title,
        'description': survey.description,
        'questions': [{
            'id': question.id,
            'text': question.question_text,
            'type': question.question_type,
            'choices': [{
                'id': choice.id,
                'text': choice.choice_text
            } for choice in question.get_choices()]
        } for question in survey.get_questions()]
    } for survey in unanswered_surveys]

    return JsonResponse(surveys_data, safe=False)

@login_required
def survey_results(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    
    # 作成者でない場合はアクセス拒否
    if request.user != survey.creator:
        raise PermissionDenied
    
    # 質問と選択肢を取得し、各選択肢の投票数を計算
    questions = []
    for question in survey.questions.all().prefetch_related('choices', 'answers__selected_choices'):
        choices_data = []
        total_votes = 0
        
        # 各選択肢の投票数を集計
        for choice in question.choices.all():
            votes = choice.answers.count()  # この選択肢が選ばれた回数
            total_votes += votes
            choices_data.append({
                'choice_text': choice.choice_text,
                'votes': votes
            })
        
        questions.append({
            'question_text': question.question_text,
            'choices': choices_data,
            'total_votes': total_votes
        })
        
        # デバッグ情報
        print(f"\nQuestion: {question.question_text}")
        print(f"Total votes: {total_votes}")
        for choice in choices_data:
            print(f"- {choice['choice_text']}: {choice['votes']} votes")
    
    context = {
        'survey': survey,
        'questions': questions,
        'total_responses': survey.current_responses,
    }
    
    return render(request, 'polls/survey_results.html', context)
