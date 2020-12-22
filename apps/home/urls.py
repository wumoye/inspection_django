from django.urls import path
from home.views import HomepageView

urlpatterns = [
    path('', HomepageView.as_view(), name='index'),  # ホームページ
    path('index', HomepageView.as_view(), name='index'),  # ホームページ
]
