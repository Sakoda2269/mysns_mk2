from django.views import generic
from .models import Post
from django.urls import reverse_lazy
from django.forms.models import BaseModelForm
from django.http import HttpResponse


class IndexView(generic.ListView):
    model = Post


class DetailView(generic.DetailView):
    model = Post


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