from django.urls import path
from . import views


app_name = "sns"


urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("post/<str:pk>/", views.DetailView.as_view(), name="post"),
    path("create/", views.CreateView.as_view(), name="create"),
    path("update/<str:pk>/", views.UpdateView.as_view(), name="update"),
    path("delete/<str:pk>/", views.DeleteView.as_view(), name="delete"),
]