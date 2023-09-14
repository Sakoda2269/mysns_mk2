from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .forms import SetPassword, ChangePassword


app_name = "accounts"


urlpatterns = [
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("user/<str:id>/", views.user_detail, name="user"),
    path("follow/<str:followed_id>/", views.follow, name="follow"),
    path("ajax_follow/", views.ajax_follow, name="ajax_follow"),
    path("follower/<str:id>/<str:follow_type>/", views.follower_list, name="follower"),
    path("goodTab/<str:id>/", views.ajax_goodtab, name="ajax_good_tab"),
    path("block/<str:id>/", views.block, name="block"),
    path("mute/<str:id>/", views.mute, name="mute"),
    path("edit/<str:pk>/", views.UpdateView.as_view(), name="edit"),
    path('password_change_form/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change.html', form_class=ChangePassword), name='password_change_form'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_finish.html'), name='password_change_done'),
    path('password_reset_form/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html', from_email='djangomysnsmail@gmail.com'), name='password_reset_form'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_mail_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirmation.html', form_class=SetPassword), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_finish.html'), name='password_reset_complete'),
]