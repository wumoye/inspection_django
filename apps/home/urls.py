from django.urls import path
from home.views import HomepageView,TestView

urlpatterns = [
    path('', HomepageView.as_view(), name='index'),  # ホームページ
    path('test', TestView.as_view(), name='test'),  # ホームページ

]
