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


def hash_mention_check(detail:str):
    from django.contrib.auth import get_user_model
    from sns.models import Hashtag
    user_tags = {}
    hashtags = {}
    for u in get_user_model().objects.all():
        user_tags[u.usertag] = u
    for h in Hashtag.objects.all():
        hashtags[h.name] = h
    mention = set()
    hash_tag = set()
    for i in range(len(detail)):
        if detail[i] == "@":
            for j in range(16, 0, -1):
                usertag = detail[i+1:i+j+1]
                if usertag in user_tags:
                    mention.add(user_tags[usertag])
                    break
        if detail[i] == "#":
                if detail[i+1] != " ":
                    for j in range(2, 18):
                        if i+j >= len(detail) or detail[i+j] == " " or detail[i+j] == "\r" or \
                            detail[i+j] == "\n" or detail[i+j] == "#" or detail[i+j] == "@":
                            target_hashtag = detail[i+1:i+j]
                            if target_hashtag in hashtags:
                                hash_tag.add(hashtags[target_hashtag])
                            else:
                                new = Hashtag.objects.create(
                                    name=target_hashtag
                                )
                                hashtags[new.name] = new
                                hash_tag.add(new)
                            break
                    else:
                        if detail[i+1:i+j] in hashtags:
                            hash_tag.add(hashtags[detail[i+1:i+j]])
                        else:
                            new = Hashtag.objects.create(
                                name=target_hashtag
                            )
                            hashtags[new.name] = new
                            hash_tag.add(target_hashtag)
    return mention, hash_tag