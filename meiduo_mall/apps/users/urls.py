from django.urls import path
from apps.users.views import UsernameCountView, MobileCountView, RegisterView,LoginView

urlpatterns = [
    # 判断用户名是否重复
    path('usernames/<username_converter:username>/count/',UsernameCountView.as_view()),
    path('mobiles/<mobile>/count/',MobileCountView.as_view()),
    path('register/',RegisterView.as_view()),
    path('login/',LoginView.as_view()),
]
