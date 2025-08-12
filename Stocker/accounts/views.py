from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError, transaction
from django.contrib import messages
from .models import Profile


def sign_up(request: HttpRequest):
    if request.method == "POST":
        try:
            with transaction.atomic():
                new_user = User.objects.create_user(
                    username=request.POST.get("username", "").strip(),
                    password=request.POST.get("password", ""),
                    email=request.POST.get("email", "").strip(),
                    first_name=request.POST.get("first_name", "").strip(),
                    last_name=request.POST.get("last_name", "").strip(),
                )
                new_user.save()

                # create profile for user
                profile = Profile(
                    user=new_user,
                    about=request.POST.get("about", "").strip(),
                )
                avatar_file = request.FILES.get("avatar")
                if avatar_file:
                    profile.avatar = avatar_file  # وإلا يبقى على default
                profile.save()

            messages.success(request, "Registered user successfully", "alert-success")
            return redirect("accounts:sign_in")

        except IntegrityError:
            messages.error(request, "Please choose another username", "alert-danger")
        except Exception as e:
            print(e)
            messages.error(request, "Couldn't register user. Try again", "alert-danger")

    return render(request, "accounts/signup.html", {})


def update_user_profile(request: HttpRequest):
    if not request.user.is_authenticated:
        messages.warning(request, "Only registered users can update their profile", "alert-warning")
        return redirect("accounts:sign_in")

    if request.method == "POST":
        try:
            with transaction.atomic():
                user: User = request.user
                user.first_name = request.POST.get("first_name", user.first_name)
                user.last_name  = request.POST.get("last_name", user.last_name)
                user.email      = request.POST.get("email", user.email)
                user.save()

                # تأكد من وجود البروفايل
                profile, _ = Profile.objects.get_or_create(user=user)
                profile.about = request.POST.get("about", profile.about)
                if "avatar" in request.FILES and request.FILES["avatar"]:
                    profile.avatar = request.FILES["avatar"]
                profile.save()

            messages.success(request, "Updated profile successfully", "alert-success")
        except Exception as e:
            print(e)
            messages.error(request, "Couldn't update profile", "alert-danger")

    return render(request, "accounts/update_profile.html")


def sign_in(request: HttpRequest):
    if request.method == "POST":
        # checking user credentials
        user = authenticate(
            request,
            username=request.POST.get("username", "").strip(),
            password=request.POST.get("password", "")
        )
        if user:
            # login the user
            login(request, user)
            messages.success(request, "Logged in successfully", "alert-success")
            return redirect(request.GET.get("next", "/"))
        else:
            messages.error(request, "Please try again. Your credentials are wrong", "alert-danger")

    return render(request, "accounts/signin.html")


def log_out(request: HttpRequest):
    logout(request)
    messages.success(request, "Logged out successfully", "alert-warning")
    return redirect(request.GET.get("next", "/"))


def user_profile_view(request: HttpRequest, user_name):
    try:
        user = User.objects.get(username=user_name)
        # أنشئ Profile لو ما كان موجود
        if not Profile.objects.filter(user=user).exists():
            Profile.objects.create(user=user)
    except Exception as e:
        print(e)
        return render(request, "404.html")

    return render(request, "accounts/profile.html", {"user": user})
