from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
import uuid


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=50)
    detail = models.CharField(max_length=255)
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    
    def __str__(self):
        return self.title
    

    def get_absolute_url(self):
        return reverse("sns:post", kwargs={'pk' : self.pk})