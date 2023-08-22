from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.urls import reverse_lazy
from .forms import SignUpForm
from .models import CustomUser, Follower, Block, Mute
from sns.models import Post, Good
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required


class SignUpView(generic.CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy("login")
    template_name = "accounts/signup.html"


def user_detail(request, id):
    context = {}
    user = get_object_or_404(CustomUser, pk=id)
    post = Post.objects.filter(author=user)
    following_num = Follower.objects.filter(following=user).count()
    followed_num = Follower.objects.filter(followed=user).count()
    context["userDetail"] = user
    context["posts"] = post
    context["following"] = False
    context["following_num"] = following_num
    context["followed_num"] = followed_num
    good_posts = []
    gooding = Good.objects.filter(gooder=user)
    for g in gooding:
        good_posts.append(g.post)
    context["good_posts"] = good_posts
    context["btn_class"] = "btn-primary"

    if request.user.is_anonymous:
        return render(request, "accounts/userDetail.html", context)
    
    following = Follower.objects.filter(followed=user, following=request.user).exists()
    context["following"] = following
    if following:
        button_class = "btn-warning"
    else :
        button_class = "btn-primary"
    context["btn_class"] = button_class
    good = Good.objects.filter(gooder=request.user)
    goods = set()
    for g in good:
        goods.add(g.post.id)
    context["goods"] = goods
    context["is_block"] = Block.objects.filter(blocker=request.user, blocked=user).exists()
    context["is_blocked"] = Block.objects.filter(blocker=user, blocked=request.user).exists()
    context["is_mute"] = Mute.objects.filter(muter=request.user, muted=user).exists()
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
    followed_num = Follower.objects.filter(followed=followed_user).count()
    context["num"] = followed_num
    return JsonResponse(context)


@login_required
def block(request, id):
    blocker = request.user
    blocked = get_object_or_404(CustomUser, id=id)
    if blocker == blocked:
        return redirect(f"/accounts/user/{id}")
    if Block.objects.filter(blocker=blocker, blocked=blocked).exists():
        Block.objects.get(blocker=blocker, blocked=blocked).delete()
    else:
        Block.objects.create(
            blocker = blocker,
            blocked = blocked
        )
    return redirect(f"/accounts/user/{id}")


@login_required
def mute(request, id):
    muter = request.user
    muted = get_object_or_404(CustomUser, id=id)
    if muter == muted:
        return redirect(f"/accounts/user/{id}")
    if Mute.objects.filter(muter=muter, muted=muted).exists():
        Mute.objects.get(muter=muter, muted=muted).delete()
    else:
        Mute.objects.create(
            muter = muter,
            muted = muted
        )
    return redirect(f"/accounts/user/{id}")


def follower_list(request, id, follow_type):
    user = get_object_or_404(CustomUser, id=id)
    context = {}
    context["followers"] = []
    if follow_type=="following":
        for follower in Follower.objects.filter(following=user):
            context["followers"].append(follower.followed)
        context["method"]=follow_type
    elif follow_type=="followed":
        for follower in Follower.objects.filter(followed=user):
            context["followers"].append(follower.following)
        context["method"]=follow_type
    return render(request, "accounts/followerList.html", context)


def ajax_goodtab(request, id):
    context = {}
    user = get_object_or_404(CustomUser, pk=id)
    post = Post.objects.filter(author=user)
    following_num = Follower.objects.filter(following=user).count()
    followed_num = Follower.objects.filter(followed=user).count()
    context["userDetail"] = user
    context["posts"] = post
    context["following"] = False
    context["following_num"] = following_num
    context["followed_num"] = followed_num
    good_posts = []
    gooding = Good.objects.filter(gooder=user)
    for g in gooding:
        good_posts.append(g.post)
    context["good_posts"] = good_posts
    context["goods"] = set()
    context["btn_class"] = "btn-primary"

    if request.user.is_anonymous:
        return render(request, "accounts/goodTab.html", context)
    
    following = Follower.objects.filter(followed=user, following=request.user).exists()
    context["following"] = following
    if following:
        button_class = "btn-warning"
    else :
        button_class = "btn-primary"
    context["btn_class"] = button_class
    good = Good.objects.filter(gooder=request.user)
    goods = set()
    for g in good:
        goods.add(g.post.id)
    context["goods"] = goods
    blocks = set()
    for b in Block.objects.filter(blocker=request.user):
        blocks.add(b.blocked)
    context["blocks"] = blocks
    blocked = set()
    for b in Block.objects.filter(blocked=request.user):
        blocked.add(b.blocker)
    context["blocked"] = blocked
    mutes = set()
    for m in Mute.objects.filter(muter=request.user):
        mutes.add(m.muted)
    context["mutes"] = mutes
    return render(request, "accounts/goodTab.html", context)

