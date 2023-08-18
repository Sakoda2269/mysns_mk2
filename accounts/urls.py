from django.urls import path
from . import views


app_name = "accounts"


urlpatterns = [
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("user/<str:id>/", views.user_detail, name="user"),
    path("follow/<str:followed_id>/", views.follow, name="follow"),
    path("ajax_follow/", views.ajax_follow, name="ajax_follow"),
    
]