from django.shortcuts import render, redirect, get_object_or_404
from .models import Theme, Idea
from .forms import IdeaForm

def index(request):
    themes = Theme.objects.all()
    return render(request, 'contest/index.html', {'themes': themes})

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
