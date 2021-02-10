from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View
from home.models import MeasurementsResults
from user.models import User, UserInfo

from utils.echarts import *
from utils.mixin import LoginRequiredMixin

##Written By Maiko on Febrary 1
import http.client, urllib.parse
import json
import sys
import cv2
import os
import numpy as np
import math
import csv
import time
import serial


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


class EmotionCheckView(View):
    def get(self, request):
        headers = {

            'Content-Type': 'application/octet-stream',
            'Ocp-Apim-Subscription-Key': '9504fa10bc1843c58d004b97448f6fb9',
        }

        eparams = urllib.parse.urlencode({
            'returnFaceId': 'true',
            'returnFaceLandmarks': 'false',
            'returnFaceAttributes': 'age,gender,emotion'
        })

        params = {

            "gender": "",
            "sadness": "",
            "neutral": "",
            "contempt": "",
            "disgust": "",
            "anger": "",
            "surprise": "",
            "fear": "",
            "happiness": "",
        }

        capture = cv2.VideoCapture(0)
        cnt = 0
        try:

            while True:
                _, frame = capture.read()
                height, width, channels = frame.shape
                ret, buf = cv2.imencode('.jpg', frame)
                conn = http.client.HTTPSConnection('test0127.cognitiveservices.azure.com')
                conn.request("POST", "/face/v1.0/detect?%s" % eparams, buf.tobytes(), headers)
                response = conn.getresponse()
                data = json.loads(response.read())
                if len(data) == 1:
                    params['gender'] = data[0]['faceAttributes']['gender']
                    body_sexial = data[0]['faceAttributes']['gender']
                    params['message'] = "検出完了！"

                    # Send the following data to the database
                    params['sadness'] = round(data[0]['faceAttributes']['emotion']['sadness'] * 100)
                    params['neutral'] = round(data[0]['faceAttributes']['emotion']['neutral'] * 100)
                    params['contempt'] = round(data[0]['faceAttributes']['emotion']['contempt'] * 100)
                    params['disgust'] = round(data[0]['faceAttributes']['emotion']['disgust'] * 100)
                    params['anger'] = round(data[0]['faceAttributes']['emotion']['anger'] * 100)
                    params['surprise'] = round(data[0]['faceAttributes']['emotion']['surprise'] * 100)
                    params['fear'] = round(data[0]['faceAttributes']['emotion']['fear'] * 100)
                    params['happiness'] = round(data[0]['faceAttributes']['emotion']['happiness'] * 100)
                    break

                if cnt >= 50:
                    params['message'] = "人を検出できません"
                    break
                cnt += 1
            capture.release()
            cv2.destroyAllWindows()
        except KeyError:
            params['message'] = "人を検出できません"
            capture.release()
            cv2.destroyAllWindows()
        except AttributeError:
            params['message'] = "人を検出できません"
            capture.release()
            cv2.destroyAllWindows()
        return render(request, 'emotion_check.html', params)

    def post(self, request):
        pass


class PulseTestView(View):

    def get(self, request):
        message = ''
        data = ' '
        fatigue_level = ''
        return render(request, 'test2.html', {'message': message, 'data': data})

    def post(self, request):
        if request.method == 'POST':
            if 'button_2' in request.POST:
                try:
                    ser = serial.Serial('/dev/cu.usbmodem14301', 9600)
                    start_time = time.time()
                    time.sleep(5)
                    while True:
                        ser_bmp = ser.readline()
                        ser_bmp = ser_bmp.strip()
                        decoded_bmp = ser_bmp.decode("utf-8")
                        if decoded_bmp == "Please Type number":
                            ser.write(bytes("3", 'utf-8'))
                        if decoded_bmp == "average_pulse":
                            ser_bmp = ser.readline()
                            ser_bmp = ser_bmp.strip()
                            decoded_bmp = ser_bmp.decode("utf-8")
                            message = '成功です！'
                            data = 'あなたの脈拍数は' + decoded_bmp + "です！"
                            break
                        print(decoded_bmp)
                        if time.time() - start_time >= 60:
                            message = '脈が取れません！'
                            data = ' '
                            break
                    if message == '脈が取れません！':
                        return render(request, 'result_pulse.html',
                                      {'message': message, 'data': data, 'fatigue_level': ''})
                    decoded_bmp = int(decoded_bmp)

                    # Check fatigue_level
                    if decoded_bmp <= 50:
                        send_fatigue_level = 3
                    elif 51 <= decoded_bmp <= 66:
                        send_fatigue_level = 2
                    elif 67 <= decoded_bmp <= 80:
                        send_fatigue_level = 1
                    elif 81 <= decoded_bmp <= 84:
                        send_fatigue_level = 2
                    elif 85 <= decoded_bmp <= 100:
                        send_fatigue_level = 3
                    else:
                        send_fatigue_level = 4

                    # Register data
                    user = request.user
                    if user == "AnoymousUser":
                        print("user is AnoymousUser")
                    else:
                        MeasurementsResults.objects.create(user_id=user.user_id, level=send_fatigue_level,
                                                           pulse=decoded_bmp)

                    fatigue_level = "あなたの健康レベルは" + str(send_fatigue_level) + "です！"

                except serial.serialutil.SerialException:
                    message = '失敗です！'
                    data = ' '
                    fatigue_level = ' '

        return render(request, 'result_pulse.html', {'message': message, 'data': data, 'fatigue_level': fatigue_level})


def get_data():
    return MeasurementsResults.objects.all().select_related().order_by("create_time")


class ChartView(View):

    def get(self, request, *args, **kwargs):
        data = get_data()
        return JsonResponse(json.loads(base_scatter(data)))


class ShowDataView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open("./templates/show_data.html").read())
