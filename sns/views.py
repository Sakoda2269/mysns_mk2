from typing import Any, Dict
from django.db.models.query import QuerySet
from django.views import generic
from .models import Post, Good, Notice, Hashtag
from accounts.models import Follower, Block, Mute
from .forms import CreatePost, CommentForm
from django.urls import reverse_lazy
from django.forms.models import BaseModelForm
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from mysns import lib
import json


class IndexView(generic.ListView):
    count = Post.objects.filter(mode=0).count()
    show_num = 5
    if count-show_num < 0:
        queryset = Post.objects.filter(mode=0)
    else :
        queryset = Post.objects.filter(mode=0)[count-show_num:]

    def get_context_data(self, *args, **kwargs: Any):
        context = super().get_context_data(*args, **kwargs)
        if self.count - self.show_num < 0:
            post = Post.objects.filter(mode=0)
        else:
            post = Post.objects.filter(mode=0)[self.count-self.show_num:]
        context["order"] = 1
        context["last"] = 0
        lib.list_comment(context, post)
        if self.request.user.is_anonymous:
            return context
        
        #ログインしている場合の追加情報
        # フォローしているユーザー
        follower = Follower.objects.filter(following=self.request.user)
        follows = set()
        for f in follower:
            follows.add(f.followed)
        follows.add(self.request.user)
        context["following"] = follows
        lib.user_info(context, self.request.user)
        return context  
    

class DetailView(generic.DetailView):
    model = Post

    def get_context_data(self, *args, **kwargs: Any):
        context = super().get_context_data(*args, **kwargs)
        post = context.get("object")
        # その投稿に対するコメント
        comments = Post.objects.filter(parent_post=post, mode=1)
        context["comments"] = comments
        
        comment_num = {}#その投稿に対するコメント数
        top_comment = {}#その当行に対するコメント
        lib.comment_num_count(post, comment_num)
        for c in comments:
            try:
                top_comment[c.id] = c.post_set.all()
            except Exception:
                top_comment[c.id] = []
        context["comment_num"] = comment_num
        context["top_comment"] = top_comment
        context["this_comment_num"] = post.post_set.all().count()
        if self.request.user.is_anonymous:
            return context
        
        #ログインしているときの追加情報
        #その投稿をイイねしているか
        good = Good.objects.filter(gooder=self.request.user)
        goods = set()
        for g in good:
            goods.add(g.post.id)
        context["goods"] = goods
        context["good"] = Good.objects.filter(gooder=self.request.user, post=post).exists()
        #ブロック関連
        context["is_block"] = Block.objects.filter(blocker=self.request.user, blocked=post.author).exists()
        context["is_blocked"] = Block.objects.filter(blocker=post.author, blocked=self.request.user).exists()
        return context
    

class CreateView(generic.edit.CreateView):
    model = Post
    form_class = CreatePost
    success_url = reverse_lazy("sns:index")

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        form.instance.author = self.request.user
        self.this = form.instance
        return super(CreateView, self).form_valid(form)
    
    def get_success_url(self) -> str:
        post = self.this
        detail = post.detail
        mentions, hashes = lib.hash_mention_check(detail)
        for m in mentions:
            Notice.objects.create(
                method="mention",
                user_from=post.author,
                user_to=m,
                post=post
            )
            post.mention.add(m)
        for h in hashes:
            h.posts.add(post)

        return super().get_success_url()

    
class UpdateView(UserPassesTestMixin, generic.edit.UpdateView):
    model = Post
    form_class = CreatePost

    def get_success_url(self) -> str:
        post = self.get_object()
        mention = set(post.mention.all())
        hashtags = set(post.hashtag_set.all())
        new_mention, new_hash = lib.hash_mention_check(post.detail)
        for u in (mention - new_mention):
            post.mention.remove(u)
            Notice.objects.get(method="mention", post=post, user_to=u).delete()
        for u in (new_mention - mention):
            post.mention.add(u)
            Notice.objects.create(
                method="mention",
                post=post,
                user_to=u,
                user_from=post.author
            )
        for h in (hashtags - new_hash):
            h.posts.remove(post)
            if h.posts.all().count() == 0:
                h.delete()
        for h in (new_hash - hashtags):
            h.posts.add(post)
        hashtags = set(post.hashtag_set.all())

        return super().get_success_url()

    def test_func(self):
        return self.get_object().author == self.request.user


class DeleteView(UserPassesTestMixin, generic.edit.DeleteView):
    model = Post
    success_url = reverse_lazy("sns:index")

    def delete(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        post = self.get_object()
        for h in post.hashtag_set.all():
            if h.posts.all().count() == 1:
                h.delete()
        return super().delete(request, *args, **kwargs)

    def test_func(self):
        return self.get_object().author == self.request.user


@login_required
def good(request, post_id, isList):
    post = get_object_or_404(Post, id=post_id)
    is_good = Good.objects.filter(gooder=request.user, post=post)
    if is_good.exists():
        if isList:
            return redirect("/sns/")
        return redirect(f"/sns/post/{post_id}")
    else:
        Good.objects.create(
            post = post,
            gooder = request.user
        )
        Notice.objects.create(
            method="good",
            user_from=request.user,
            user_to=post.author,
            post=post
        )
        post.good_num+=1
        post.save()
    
    if isList:
        return redirect("/sns/")
    return redirect(f"/sns/post/{post_id}")


def ajax_good(request):
    post_id = request.POST['post_id']
    post = get_object_or_404(Post, id=post_id)
    good = Good.objects.filter(post=post, gooder=request.user)
    context = {}
    if good.exists():
        good.delete()
        notice = get_object_or_404(Notice, method="good", user_from=request.user, post=post)
        notice.delete()
        post.good_num-=1
        post.save()
        context["method"] = "delete"
    else:
        Good.objects.create(
            post=post,
            gooder=request.user
        )
        Notice.objects.create(
            method="good",
            user_from=request.user,
            user_to=post.author,
            post=post
        )
        post.good_num+=1
        post.save()
        context["method"] = "create"
    context["num"] = str(post.good_num)
    return JsonResponse(context)


def ajax_comment(request):
    post_id = request.POST['post_id']
    comment = request.POST['comment']
    post = Post.objects.get(id=post_id)
    post_title = post.title + "のコメント",
    if post.mode == 1:
        post_title = post.title
    comment = Post.objects.create(
        author=request.user,
        title=post_title,
        detail=comment,
        mode=1,
        parent_post = post
    )
    Notice.objects.create(
        method="comment",
        user_from=request.user,
        user_to=post.author,
        post=post,
        comment=comment
    )
    
    context = {}
    context["comment_num"] = post.post_set.all().count()
    return JsonResponse(context)


def ajax_comment_list(request, id):
    context = {}
    comments = Post.objects.filter(mode=1, parent_post=Post.objects.get(id=id))
    context["comments"] = comments
    good = Good.objects.filter(gooder=request.user)
    goods = set()
    for g in good:
        goods.add(g.post.id)
    context["goods"] = goods
    comment_num = {}
    for c in comments:
        comment_num[c.id] = c.post_set.all().count()
    context["comment_num"] = comment_num
    return render(request, "sns/comment_list.html", context)

def good_user(request, id):
    post = get_object_or_404(Post, id=id)
    good_user = Good.objects.filter(post=post)
    good_users = []
    for g in good_user:
        good_users.append(g.gooder)
    context = {
        "gooders":good_users
    }
    
    return render(request, "sns/good_user.html", context)


class Comment(generic.edit.CreateView):
    model = Post
    form_class = CommentForm
    template_name = "sns/comment_form.html"
    success_url = reverse_lazy("sns:index")

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        form.instance.mode = 1
        form.instance.author = self.request.user
        id = self.kwargs["pk"]
        form.instance.parent_post = get_object_or_404(Post, id=id)
        return super(Comment, self).form_valid(form)


def notification(request, id):
    context = {}
    user = get_object_or_404(get_user_model(), id=id)
    notice_list = Notice.objects.filter(user_to = user)
    news = set()
    for n in notice_list:
        if n.new:
            n.new = False
            news.add(n)
            n.save()
    context["notices"] = notice_list
    context["news"] = news
    return render(request, "sns/notice.html", context)


def check_notification(request):
    context = {}
    user_id = request.POST["user_id"]
    user = get_object_or_404(get_user_model(), id=user_id)
    news = Notice.objects.filter(user_to=user, new=True)
    context["exist"] = news.exists()
    return JsonResponse(context)


def search(request, tag=""):
    context = {}
    hashtags = {"data":[]}
    for h in Hashtag.objects.all():
        hashtags["data"].append(h.name)
    context["data"] = json.dumps(hashtags)
    context["tag"] = "#" + tag
    return render(request, "sns/search.html", context)


def ajax_show_hash(request, name):
    hashtag = get_object_or_404(Hashtag, name=name)
    context = {}
    hash_posts = hashtag.posts.all()

    # イイねタブに表示する投稿
    context["hash_posts"] = hash_posts
    lib.list_comment(context, hash_posts)

    if request.user.is_anonymous:
        return render(request, "sns/hash_posts.html", context)
    
    #ログインしているときの追加情報
    lib.user_info(context, request.user)
    return render(request, "sns/hash_posts.html", context)


def ajax_additional_post(request, id):
    show_num = 5
    count = Post.objects.all().count()
    order = int(id) + 1
    context = {}
    context["order"] = order
    context["last"] = 0
    if count < show_num * order:
        post = Post.objects.filter(mode=0)[:count - show_num * (order-1) + 1]
        context["last"] = 1
    else:
        post = Post.objects.filter(mode=0)[count - show_num * order + 1 : count - show_num * (order-1) + 1]
    context["object_list"] = post
    lib.list_comment(context, post)
    if request.user.is_anonymous:
        return render(request, "sns/additional_post_list.html", context)
    
    #ログインしているときの追加情報
    lib.user_info(context, request.user)
    return render(request, "sns/additional_post_list.html", context)

    