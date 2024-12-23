from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

def home(request):
    return render(request, 'entrance/home.html')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('entrance:home')
    else:
        form = UserCreationForm()
    return render(request, 'entrance/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('entrance:home')
    else:
        form = AuthenticationForm()
    return render(request, 'entrance/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('entrance:home')