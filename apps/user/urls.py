from django.urls import path
from user.views import RegisterView, LoginView, ActiveView, MypageView

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),  # 新規登録
    path('login', LoginView.as_view(), name='login'),  # ログイン
    path('active/<token>', ActiveView.as_view(), name='active'),  # アクティブ
    path('mypage', MypageView.as_view(), name='mypage'),  # ユーザページ

]
