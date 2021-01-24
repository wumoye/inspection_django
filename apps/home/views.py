from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View
from home.models import MeasurementsResults
from user.models import User, UserInfo

from utils.mixin import LoginRequiredMixin


# Create your views here.

class HomepageView(LoginRequiredMixin, View):
    """ホームページ"""

    def get(self, request):
        user = request.user
        if user == "AnoymousUser":
            print("user is AnoymousUser")
            measurements_data = MeasurementsResults.objects.filter()
        else:
            userinfo = UserInfo.objects.get(id=user.user_id)
            nick_name = userinfo.nickname
            measurements_data = MeasurementsResults.objects.filter(user=user.user_id)

        return render(request, 'index.html',
                      {'page': 'index', 'measurements_data': measurements_data, 'nickname': nick_name})

    def post(self, request):
        user = request.user
        user_id = user.user_id
        measurements_data = MeasurementsResults()
        measurements_data.user = UserInfo.objects.get(id=user_id)

        measurements_data.level = request.POST.get('health_level')
        measurements_data.pulse = request.POST.get('pulse')
        print(f"level is {measurements_data.level}\npulse is {measurements_data.pulse}")
        measurements_data.save()
        return redirect(reverse('home:index'))


class TestView(View):
    def get(self, request):
        user = request.user
        nick_name = request.COOKIES.get('nickname')
        # userinfo = UserInfo.objects.get(id=user.user_id)
        # nick_name = userinfo.nickname
        measurements_data = MeasurementsResults.objects.all().select_related()

        return render(request, 'test.html',
                      {'page': 'test', 'measurements_data': measurements_data, 'nickname': nick_name})
