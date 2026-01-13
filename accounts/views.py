from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from .models import Profile
from .forms import SignupForm

def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password1"],
                first_name=form.cleaned_data["full_name"],
            )
            Profile.objects.create(user=user, phone_number=form.cleaned_data["phone_number"])
            login(request, user)   # 註冊完直接登入
            return redirect("/")
    else:
        form = SignupForm()

    return render(request, "accounts/signup.html", {"form": form})
