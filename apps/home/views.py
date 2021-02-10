from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View
from home.models import MeasurementsResults
from user.models import User, UserInfo

from utils.echarts import *
from utils.mixin import LoginRequiredMixin

# Create your views here.

class HomepageView(LoginRequiredMixin, View):
    """ホームページ"""

    def get_nickname(self, request):
        user = request.user
        userinfo = UserInfo.objects.get(id=user.user_id)
        nick_name = userinfo.nickname
        return nick_name

    def get(self, request):
        user = request.user
        if user == "AnoymousUser":
            print("user is AnoymousUser")
            # measurements_data = MeasurementsResults.objects.filter()
        else:
            nick_name = self.get_nickname(request)
            measurements_data = MeasurementsResults.objects.filter(user=user.user_id).order_by("-create_time")

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
        if not all([measurements_data.level, measurements_data.pulse]):
            nick_name = self.get_nickname(request)
            measurements_data = MeasurementsResults.objects.filter(user=user.user_id).order_by("-create_time")
            return render(request, 'index.html',
                          {'page': 'index', 'measurements_data': measurements_data, 'nickname': nick_name,
                           'errmsg': 'データが不完全'})
        measurements_data.save()
        return redirect(reverse('home:index'))


class TestView(View):
    def get(self, request):
        user = request.user
        nick_name = request.COOKIES.get('nickname')
        if nick_name is None:
            nick_name = request.COOKIES.get('username')
        # userinfo = UserInfo.objects.get(id=user.user_id)
        # nick_name = userinfo.nickname
        measurements_data = MeasurementsResults.objects.all().select_related()

        return render(request, 'test.html',
                      {'page': 'test', 'measurements_data': measurements_data, 'nickname': nick_name})


class Test2View(View):
    def get(self, request):
        return render(request, 'test2.html')


def get_data():
    return MeasurementsResults.objects.all().select_related().order_by("create_time")


class ChartView(View):

    def get(self, request, *args, **kwargs):
        data = get_data()
        return JsonResponse(json.loads(base_scatter(data)))


class IndexView(View):
    def get(self, request, *args, **kwargs):
        print(f'start get indexview')
        return HttpResponse(content=open("./templates/show_data.html").read())
