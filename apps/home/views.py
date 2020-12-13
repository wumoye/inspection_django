from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View
from user.models import MeasurementResults
from user.models import User


# Create your views here.


class HomepageView(View):
    '''ホームページ'''

    def get(self, request):
        return render(request, 'index.html')

    def post(self, request):
        username = request.user

        measurement_date = MeasurementResults()
        measurement_date.user = User.objects.get(username=username)

        measurement_date.pulse = request.POST.get('pulse_test')
        measurement_date.level = request.POST.get('level_test')

        measurement_date.save()
        return redirect(reverse('home:index'))
