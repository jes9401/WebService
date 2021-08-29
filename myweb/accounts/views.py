from django.shortcuts import render, redirect
import json
from django.views import View
from django.http import JsonResponse
from accounts.serializers import ProfileSerializer
from .models import Profile
from django.contrib.auth.models import User
from rest_framework import viewsets
from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm

from .forms import UserUpdateForm, ProfileUpdateForm


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    def post(self, request, format=None):
        return Response("ok")


def home(request):
    return render(request, 'accounts/home.html')


# def register(request):
#     if request.method == 'POST':
#         form = UserRegisterForm(request.POST)
#         if form.is_valid():
#             form.save()
#             username = form.cleaned_data.get('username')
#             messages.success(request, f'Your account has been created! You are now able to log in')
#             return redirect('accounts:home')
#     else:
#         form = UserRegisterForm()
#     return render(request, 'accounts/register.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created! You are now able to log in')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, '업데이트 됐습니다!')
            return redirect('profile')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    th = request.user.profile.twohand
    waist = request.user.profile.waist
    context = {
        'u_form': u_form,
        'p_form': p_form,
        'th':th,
        'waist':waist
    }

    return render(request, 'accounts/profile.html', context)


def getUser(request):
    if request.method == 'GET':
        #profile = Profile.objects.order_by('created_date').reverse()
        user=User.objects.all().order_by('id')
        profile_data = {}
        for i in range(len(user)):
            profile_data[i]=user[i].username
        #profile_data['user'] = user
        return JsonResponse(profile_data) # json으로 응답
        #return HttpResponse(json.dumps(home_data), content_type="application/json")
        #return render(request, 'uleung/getHomeInfo.html', json.dumps(home_data))
    elif request.method == 'POST':
        pass


#def signup(request):
#    if request.method=="POST":
#        if request.POST["password1"] == request.POST["password2"]:
#            user = User.objects.create_user(
#                username=request.POST["username"], password=request.POST["password1"])
#            auth.login(request,user)
#            return redirect('accounts:home')
#        return render(request, 'accounts/signup.html')
#    return render(request, 'accounts/signup.html')




#def login(request):
#    if request.method == "POST":
#        username = request.POST['username']
#        password = request.POST['password']
#        user = auth.authenticate(request,username=username, password=password)
#        if user is not None:
#            auth.login(request, user)
#            return redirect('accounts:home')
#       else:
#           return render(request, 'accounts/login.html', {'error' : 'username or password is incorrect'})
#    else:
#        return render(request, 'accounts/login.html')

#def logout(request):
#   auth.logout(request)
#    return redirect('accounts:home')
