from django.shortcuts import render, redirect, get_object_or_404
from .models import Theme, Idea
from .forms import IdeaForm
from datetime import datetime

def index(request):
    # 現在の年月を取得
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    
    # テーマ（後でAPIから取得する予定）
    current_theme = "無駄から始まるイノベーション!!"
    
    # テーマ一覧（既存のコード）
    themes = Theme.objects.all().prefetch_related(
        'idea_set',
        'idea_set__author',
        'idea_set__likes'
    )
    
    return render(request, 'contest/index.html', {
        'themes': themes,
        'current_year': current_year,
        'current_month': current_month,
        'current_theme': current_theme,
    })

def submit_idea(request):
    if request.method == 'POST':
        form = IdeaForm(request.POST)
        if form.is_valid():
            idea = form.save(commit=False)
            idea.author = request.user
            idea.save()
            return redirect('contest:index')
    else:
        form = IdeaForm()
    return render(request, 'contest/submit_idea.html', {'form': form})

def like_idea(request, idea_id):
    idea = get_object_or_404(Idea, id=idea_id)
    if request.user in idea.likes.all():
        idea.likes.remove(request.user)
    else:
        idea.likes.add(request.user)
    return redirect('contest:index')
