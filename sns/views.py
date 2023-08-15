from typing import Any, Dict
from django.db.models.query import QuerySet
from django.views import generic
from .models import Post, Good
from django.urls import reverse_lazy
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect


class IndexView(generic.ListView):
    model = Post


    def get_context_data(self, *args, **kwargs: Any):
        context = super().get_context_data(*args, **kwargs)
        good = Good.objects.filter(gooder=self.request.user)
        tmp = set()
        numdict = {}
        for m in Post.objects.all():
            numdict[str(m.id)] = m.id
        for g in good:
            tmp.add(g.post)
        context["goods"] = tmp
        context["num"] = numdict
        return context  
    

class DetailView(generic.DetailView):
    model = Post


    def get_context_data(self, *args, **kwargs: Any):
        context = super().get_context_data(*args, **kwargs)
        post = context.get("object")
        context["goods"] = len(Good.objects.filter(gooder=self.request.user, post=post))
        return context
    

class CreateView(generic.edit.CreateView):
    model = Post
    fields = ["title", "detail"]


    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        form.instance.author = self.request.user
        return super(CreateView, self).form_valid(form)

class UpdateView(generic.edit.UpdateView):
    model = Post
    fields = ["title", "detail"]


class DeleteView(generic.edit.DeleteView):
    model = Post
    success_url = reverse_lazy("sns:index")


def good(request, post_id, isList):
    post = get_object_or_404(Post, id=post_id)
    is_good = Good.objects.filter(gooder=request.user, post=post)
    if(len(is_good)):
        is_good.delete()
        post.good_num-=1
        post.save()
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
