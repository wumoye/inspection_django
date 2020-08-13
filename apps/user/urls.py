from django.urls import path
from user.views import RegisterView, LoginView

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),  # 新規登録
    path('login', LoginView.as_view(), name='login'),  # ログイン
]
