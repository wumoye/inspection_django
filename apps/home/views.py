from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View
from home.models import MeasurementResults
from user.models import User

from utils.mixin import LoginRequiredMixin


# Create your views here.


class HomepageView(LoginRequiredMixin, View):
    '''ホームページ'''

    def get(self, request):
        user = request.user
        print(user)
        if user == "AnoymousUser":
            print("user is AnoymousUser")
            measur_datas = MeasurementResults.objects.filter()
        else:
            measur_datas = MeasurementResults.objects.filter(user=user)

        return render(request, 'index.html', {'page': 'index', 'measur_datas': measur_datas, 'username': user})

    def post(self, request):
        username = request.user

        measurement_date = MeasurementResults()
        measurement_date.user = User.objects.get(username=username)

        measurement_date.level = request.POST.get('health_level')
        measurement_date.pulse = request.POST.get('pulse')
        print(f"level is {measurement_date.level}\npulse is {measurement_date.pulse}")
        measurement_date.save()
        return redirect(reverse('home:index'))

class TestView(View):
    def get(self, request):
        user = request.user
        measur_datas = MeasurementResults.objects.filter()
        return render(request, 'test.html', {'page': 'index', 'measur_datas': measur_datas, 'username': user})