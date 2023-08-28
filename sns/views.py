from typing import Any, Dict
from django.db.models.query import QuerySet
from django.views import generic
from .models import Post, Good
from accounts.models import Follower, Block, Mute
from .forms import CreatePost, CommentForm
from django.urls import reverse_lazy
from django.forms.models import BaseModelForm
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin

class IndexView(generic.ListView):
    queryset = Post.objects.filter(mode=0)

    def get_context_data(self, *args, **kwargs: Any):
        context = super().get_context_data(*args, **kwargs)
        comments = {}
        com = Post.objects.filter(mode=1)
        for c in com:
            if c.parent_post.id not in comments:
                comments[c.parent_post.id] = []
            comments[c.parent_post.id].append(c)
        context["post_comments"] = comments
        if self.request.user.is_anonymous:
            return context
        good = Good.objects.filter(gooder=self.request.user)
        goods = set()
        for g in good:
            goods.add(g.post.id)
        follower = Follower.objects.filter(following=self.request.user)
        follows = set()
        for f in follower:
            follows.add(f.followed)
        follows.add(self.request.user)
        context["goods"] = goods
        context["following"] = follows
        blocks = set()
        for b in Block.objects.filter(blocker=self.request.user):
            blocks.add(b.blocked)
        context["blocks"] = blocks
        blocked = set()
        for b in Block.objects.filter(blocked=self.request.user):
            blocked.add(b.blocker)
        context["blocked"] = blocked
        mutes = set()
        for m in Mute.objects.filter(muter=self.request.user):
            mutes.add(m.muted)
        context["mutes"] = mutes
        return context  
    

class DetailView(generic.DetailView):
    model = Post

    def get_context_data(self, *args, **kwargs: Any):
        context = super().get_context_data(*args, **kwargs)
        if self.request.user.is_anonymous:
            return context
        post = context.get("object")
        context["goods"] = Good.objects.filter(gooder=self.request.user, post=post).exists()
        context["is_block"] = Block.objects.filter(blocker=self.request.user, blocked=post.author).exists()
        context["is_blocked"] = Block.objects.filter(blocker=post.author, blocked=self.request.user).exists()
        context["comments"] = Post.objects.filter(parent_post=post, mode=1)
        return context
    

class CreateView(generic.edit.CreateView):
    model = Post
    form_class = CreatePost

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
        post.good_num-=1
        post.save()
        context["method"] = "delete"
    else:
        Good.objects.create(
            post = post,
            gooder = request.user
        )
        post.good_num+=1
        post.save()
        context["method"] = "create"
    context["num"] = str(post.good_num)
    return JsonResponse(context)


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

