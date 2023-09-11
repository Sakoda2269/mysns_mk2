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
        on_delete=models.CASCADE,
        related_name="author"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    good_num = models.IntegerField(default=0)
    mode = models.IntegerField(default=0)#0:通常の投稿 1:コメント
    parent_post = models.ForeignKey(
        "Post",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
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


class Notice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    method = models.CharField(max_length=20)
    user_from = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="user_from"
    )
    user_to = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="user_to"
    )
    new = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        null=True,
        related_name="notice_post"
    )
    comment = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comment",
        null=True
    )


class Hashtag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=16)
    posts = models.ManyToManyField(
        Post,
        related_name="posts",
        blank=True
    )
