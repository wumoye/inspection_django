from django.urls import path
from home.views import HomepageView, TestView, Test2View, ChartView, IndexView

urlpatterns = [
    path('', HomepageView.as_view(), name='index'),  # ホームページ
    path('test', TestView.as_view(), name='test'),  # ホームページ
    path('test2', Test2View.as_view(), name='test2'),

    path('bar', ChartView.as_view(), name='home'),
    path('show_data', IndexView.as_view(), name='show_data'),
    path('index.html', HomepageView.as_view(), name='index'),

]
