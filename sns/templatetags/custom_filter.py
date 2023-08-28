from django import template


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