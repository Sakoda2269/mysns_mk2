def comment_num_count(now, com_num, count=0):
    ans = 0
    for n in now.post_set.all():
        ans += comment_num_count(n, com_num, count)
    com_num[now.id] = ans
    return ans + 1