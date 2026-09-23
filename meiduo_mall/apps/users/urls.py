from django.urls import path
from apps.users.views import UsernameCountView, RegisterView

urlpatterns = [
    # 判断用户名是否重复
    path('usernames/<username:username>/count/',UsernameCountView.as_view()),
    path('register/',RegisterView.as_view()),
]

