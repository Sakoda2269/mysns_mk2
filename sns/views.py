from typing import Any, Dict
from django.db.models.query import QuerySet
from django.views import generic
from .models import Post, Good, Notice
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
    queryset = Post.objects.filter(mode=0)

    def get_context_data(self, *args, **kwargs: Any):
        context = super().get_context_data(*args, **kwargs)
        post = Post.objects.filter(mode=0)
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
        return super(CreateView, self).form_valid(form)
    
    
class UpdateView(UserPassesTestMixin, generic.edit.UpdateView):
    model = Post
    form_class = CreatePost

    def test_func(self):
        return self.get_object().author == self.request.user


class DeleteView(UserPassesTestMixin, generic.edit.DeleteView):
    model = Post
    success_url = reverse_lazy("sns:index")

    def delete(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        post = self.get_object()
        if post.mode == 1:
            notice = get_object_or_404(Notice, method="comment", user_from=request.user, post=post.parent_post)
            notice.delete()
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
    Post.objects.create(
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
        post=post
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
    context["notices"] = notice_list
    return render(request, "sns/notice.html", context)
