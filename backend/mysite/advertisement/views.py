from django.shortcuts import render
from django.http import JsonResponse
from polls.models import Survey  # Surveyモデルをインポート

# ユーザーの未回答かつ回答可能なアンケートを取得するビュー
def get_unanswered_surveys(request):
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