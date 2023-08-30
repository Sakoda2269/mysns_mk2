from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
import uuid


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=50, null=True)
    detail = models.TextField(max_length=255)
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    good_num = models.IntegerField(default=0)
    mode = models.IntegerField(default=0)#0:通常の投稿 1:コメント
    parent_post = models.ForeignKey(
        "Post",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    def __str__(self):
        if self.title == None:
            return "comment"
        return self.title
    

    def get_absolute_url(self):
        return reverse("sns:post", kwargs={'pk' : self.pk})


class Good(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE
    )
    gooder = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE
    )


    def __str__(self):
        return self.post.title
