from django.contrib import admin
from .models import Post, Good, Notice, Hashtag


admin.site.register(Post)
admin.site.register(Good)
admin.site.register(Notice)
admin.site.register(Hashtag)
