from django.urls import path
from home.views import HomepageView,TestView,Test2View

urlpatterns = [
    path('', HomepageView.as_view(), name='index'),  # ホームページ
    path('test', TestView.as_view(), name='test'),  # ホームページ
    path('test2', Test2View.as_view(), name='test2'),

]
