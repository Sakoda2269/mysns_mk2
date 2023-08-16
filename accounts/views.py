from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.urls import reverse_lazy
from .forms import SignUpForm
from .models import CustomUser, Follower
from sns.models import Post
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required


class SignUpView(generic.CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy("login")
    template_name = "accounts/signup.html"


def user_detail(request, id):
    user = get_object_or_404(CustomUser, pk=id)
    post = Post.objects.filter(author=user)
    if request.user.is_anonymous:
        context = {
            "userDetail":user,
            "posts":post,
            "following":False,
        }
        return render(request, "accounts/userDetail.html", context)
    following = Follower.objects.filter(followed=user, following=request.user).exists()
    if following:
        button_class = "btn-warning"
    else :
        button_class = "btn-primary"
    context = {
        "userDetail":user,
        "posts":post,
        "following":following,
        "btn_class":button_class,
    }
    return render(request, "accounts/userDetail.html", context)


@login_required
def follow(request, followed_id):
    following_user = request.user #フォローする人
    followed_user = get_object_or_404(CustomUser, id=followed_id) #フォローされる人
    if following_user == followed_user:
        return redirect(f"/accounts/user/{followed_user.id}")
    already_followed = Follower.objects.filter(following=following_user, followed=followed_user).exists()
    if already_followed:
        Follower.objects.get(following=following_user, followed=followed_user).delete()
    else:
        Follower.objects.create(following=following_user, followed=followed_user)
    return redirect(f"/accounts/user/{followed_user.id}")


def ajax_follow(request):
    following_user = request.user
    followed_id = request.POST["followed_user_id"]
    followed_user = get_object_or_404(CustomUser, id=followed_id)
    already_followed = Follower.objects.filter(following=following_user, followed=followed_user).exists()
    context = {}
    if already_followed:
        Follower.objects.get(following=following_user, followed=followed_user).delete()
        context["method"] = "unfollow"
    else:
        Follower.objects.create(following=following_user, followed=followed_user)
        context["method"] = "follow"
    return JsonResponse(context)
