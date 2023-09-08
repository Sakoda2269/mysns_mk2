from django import template
from django.contrib.auth import get_user_model
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.urls import reverse

register = template.Library()


@register.filter
def get_value(d, k):
    if k in d:
        return d[k]
    return None


@register.filter
def following_post(posts, following):
    res = []
    for post in posts:
        if post.author in following:
            res.append(post)
    return res


@register.filter
def mention(post):
    detail = post.detail
    users = set(get_user_model().objects.all())
    usertags = {}
    for u in users:
        usertags[u.usertag] = u.id
    res = ""
    detail = escape(detail)
    i = 0
    last_i = 0
    while i < len(detail) - 1:
        if detail[i] == "@":
            for j in range(16, 0, -1):
                tag = detail[i+1:i+j+1]
                if tag in usertags:
                    res += detail[last_i:i]
                    post.mentions.add(usertags[tag])
                    res += "<a href='{}'>".format(reverse("accounts:user", kwargs=dict(id=str(usertags[tag]))))
                    res += "@" + tag
                    res += "</a>"
                    i += j
                    last_i = i + 1
                    break
        i += 1
    res += detail[last_i:]
    return mark_safe(res)
            
