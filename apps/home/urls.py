from django.urls import path
from home.views import HomepageView, TestView, ChartView, ShowDataView, EmotionCheckView, PulseTestView

urlpatterns = [
    path('', HomepageView.as_view(), name='index'),  # ホームページ
    path('test', TestView.as_view(), name='test'),  # ホームページ
    path('result_pulse', PulseTestView.as_view(), name='result_pulse'),
    path('emotion_check', EmotionCheckView.as_view(), name='emotion_check'),
    path('bar', ChartView.as_view(), name='home'),
    path('show_data', ShowDataView.as_view(), name='show_data'),
    path('index.html', HomepageView.as_view(), name='index'),

]
