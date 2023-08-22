from django.urls import path
from . import views


app_name = "accounts"


urlpatterns = [
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("user/<str:id>/", views.user_detail, name="user"),
    path("follow/<str:followed_id>/", views.follow, name="follow"),
    path("ajax_follow/", views.ajax_follow, name="ajax_follow"),
    path("follower/<str:id>/<str:follow_type>", views.follower_list, name="follower"),
    path("goodTab/<str:id>/", views.ajax_goodtab, name="ajax_good_tab"),
    path("block/<str:id>", views.block, name="block"),
    path("mute/<str:id>", views.mute, name="mute"),
]