from django.urls import path
from user.views import RegisterView, LoginView, LogoutView, ActiveView, MypageView, TestView,UserInfoView

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),  # 新規登録

    path('login', LoginView.as_view(), name='login'),  # ログイン
    path('logout', LogoutView.as_view(), name='logout'),

    path('active/<token>', ActiveView.as_view(), name='active'),  # アクティブ
    # path('', UserInfoView.as_view(), name='user'),  # アクティブ

    path('mypage', MypageView.as_view(), name='mypage'),  # ユーザページ

    path('test', TestView.as_view(), name='test'),  # test

]
