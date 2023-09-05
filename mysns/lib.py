def comment_num_count(now, com_num, count=0):
    ans = 0
    for n in now.post_set.all():
        ans += comment_num_count(n, com_num, count)
    com_num[now.id] = ans
    return ans + 1


def list_comment(context, post):
    comment_num = {} #各投稿に対するコメント数
    top_comment = {} #各投稿に対するコメント
    for p in post:
        comment_num_count(p, comment_num)
        try:
            top_comment[p.id] = p.post_set.all()
        except Exception:
            top_comment[p.id] = []
    context["comment_num"] = comment_num
    context["top_comment"] = top_comment


def user_info(context, user):
    from sns.models import Good
    from accounts.models import Block, Mute
    good = Good.objects.filter(gooder=user)
    goods = set()
    for g in good:
        goods.add(g.post.id)
    context["goods"] = goods
    # ブロックしているかどうか
    blocks = set()
    for b in Block.objects.filter(blocker=user):
        blocks.add(b.blocked)
    context["blocks"] = blocks
    # ブロックされているかどうか
    blocked = set()
    for b in Block.objects.filter(blocked=user):
        blocked.add(b.blocker)
    context["blocked"] = blocked
    # ミュートしているかどうか
    mutes = set()
    for m in Mute.objects.filter(muter=user):
        mutes.add(m.muted)
    context["mutes"] = mutes