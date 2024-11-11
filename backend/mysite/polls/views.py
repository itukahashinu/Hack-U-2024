from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import get_object_or_404, render
from .models import Question, Choice
from django.http import Http404
#####################
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import SurveySerializer
import requests
#####################
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Question
from .serializers import QuestionSerializer
#####################

"""
def index(request):
    latest_question_list = Question.objects.order_by("-pub_date")[:5]
    context = {"latest_question_list": latest_question_list}
    return render(request, "polls/index.html", context)

def detail(request, question_id):
    try:
        question = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        raise Http404("Question does not exist")
    return render(request, "polls/detail.html", {"question": question})

def results(request, question_id):
    try:
        question = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        raise Http404("Question does not exist")
    return render(request, "polls/results.html", {"question": question})

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # 選択肢が選ばれていない場合、エラーメッセージを表示する
        return render(request, 'polls/vote.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        # 投票数を増加し、結果ページにリダイレクトする
        selected_choice.votes += 1
        selected_choice.save()
        # リダイレクトを使って、ユーザーが二重送信するのを防ぐ
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))



###########################
# Google Forms APIへのリクエストを送る
def create_google_form(survey_data):
    # Google Forms APIに必要なデータを整形
    form_data = {
        'title': survey_data['title'],
        'description': survey_data['description'],
        'questions': survey_data['questions']
    }
    
    # 実際のGoogle Forms APIの呼び出し（仮のURLとAPIキー）
    api_url = "https://forms.googleapis.com/v1/forms"
    headers = {
        "Authorization": "Bearer YOUR_GOOGLE_API_KEY",  # 実際のAPIキーを使用
        "Content-Type": "application/json"
    }
    
    response = requests.post(api_url, json=form_data, headers=headers)

    if response.status_code == 200:
        # フォーム作成成功時、フォームIDを返す（仮のID）
        form_id = response.json().get('id', 'sample_form_id')
        return form_id
    else:
        # エラー処理（仮）
        return None


@api_view(['POST'])
def create_survey(request):
    """
    #アンケート作成用APIエンドポイント
    #フロントエンドから送られたアンケートデータを受け取り、Google Forms APIでフォームを作成
"""
    if request.method == 'POST':
        serializer = SurveySerializer(data=request.data)
        
        if serializer.is_valid():
            # バリデーションが成功した場合、Google Formを作成
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

            # Google Formを作成する
            google_form_id = create_google_form(survey_data)
            
            if google_form_id:
                return Response({
                    'message': 'Survey created successfully!',
                    'google_form_id': google_form_id,  # Google FormsのIDを返す
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'message': 'Failed to create the survey form.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            # バリデーションエラーが発生した場合
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
"""
##########################
# Google Forms APIのモック関数
def create_google_form_mock(survey_data):
    """
    Google Forms APIのリクエストをモックする関数
    実際のGoogle Forms APIのリクエストは行わず、仮のIDを返す
    """
    # モックデータとして、成功したフォームIDを返す
    print("Mocked create_google_form called with survey data:", survey_data)
    
    # モックされたフォームID
    return "mock_form_id_12345"

##########################

def index(request):
    latest_question_list = Question.objects.order_by("-pub_date")[:5]
    context = {"latest_question_list": latest_question_list}
    return render(request, "polls/index.html", context)

def detail(request, question_id):
    try:
        question = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        raise Http404("Question does not exist")
    return render(request, "polls/detail.html", {"question": question})

def results(request, question_id):
    try:
        question = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        raise Http404("Question does not exist")
    return render(request, "polls/results.html", {"question": question})

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # 選択肢が選ばれていない場合、エラーメッセージを表示する
        return render(request, 'polls/vote.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        # 投票数を増加し、結果ページにリダイレクトする
        selected_choice.votes += 1
        selected_choice.save()
        # リダイレクトを使って、ユーザーが二重送信するのを防ぐ
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
