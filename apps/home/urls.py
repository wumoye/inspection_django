from django.urls import path
from home.views import HomepageView
from home import views

urlpatterns = [
    path('', HomepageView.as_view(), name='index'),  # ホームページ

]
