from django import forms
from .models import Post
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from .models import Post


class CreatePost(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("title", "detail", )
        error_messages = {
            "comment" : {
                "max_length" : "コメントの文字数が" + str(Post.title.field.max_length) + "文字を超えています",
                "required" : "コメントを入力してください",
            },
        }
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs = {'placeholder': 'title', 'class': 'form-control'}
        self.fields['detail'].widget.attrs = {'placeholder': 'detail',  'class': 'form-control', 'rows': '10'}
    