import json

from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.views.generic import View
from django.urls import reverse
from django.http import HttpResponse, QueryDict
from user.models import User, UserInfo
from django.conf import settings

from celery_tasks.tasks import send_register_active_email
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
import re

from home.models import MeasurementsResults
from utils.mixin import LoginRequiredMixin

from django.contrib.auth.backends import ModelBackend
from user import models
from django.db.models import Q

import hashlib

import time
import serial
# Create your views here.

def name_to_psw(input_name):
    fingerprint_key = settings.FINGERPRINT_KEY
    name_to_pw = str(input_name) + fingerprint_key
    return hashlib.md5(name_to_pw.encode()).hexdigest()


def con_status():
    fingerprint_sensor_state = False
    is_connect = True
    if is_connect:
        fingerprint_sensor_state = True
    return fingerprint_sensor_state


def get_finger_code():
    """指紋の番号の獲得"""
    try:
        ser = serial.Serial('/dev/cu.usbmodem14301', 9600)
        start_time = time.time()
        time.sleep(5)
        while True:
            ser_bmp = ser.readline()
            ser_bmp = ser_bmp.strip()
            decoded_bmp = ser_bmp.decode("utf-8")
            print(decoded_bmp)
            if decoded_bmp == "Please Type number":
                ser.write(bytes("1", 'utf-8'))
            if decoded_bmp == "Please write your choiced number":
                person_num = UserInfo.objects.count()
                person_num += 1
                ser.write(bytes(str(person_num), 'utf-8'))
            # if Please write your choiced number
            if decoded_bmp == "Stored!":
                fingerprint_code = person_num
                break
            if decoded_bmp == "error":
                fingerprint_code = -1
                break
            if time.time() - start_time >= 60:
                fingerprint_code = -1
                break
    except serial.serialutil.SerialException:
        fingerprint_code = -1
        # fingerprint_code = 10
    '''
    if con_status():
        # get fingerprint code
        if True:
            try:
                ser=serial.Serial('/dev/cu.usbmodem14301',9600)
                start_time = time.time()
                time.sleep(5)
                while True:
                    ser_bmp=ser.readline()
                    ser_bmp=ser_bmp.strip()
                    decoded_bmp=ser_bmp.decode("utf-8")
                    if decoded_bmp == "Please Type number":
                        ser.write(bytes("2",'utf-8'))
                    if decoded_bmp == "YourFingerID:" :
                        ser_bmp=ser.readline()
                        ser_bmp=ser_bmp.strip()
                        decoded_bmp=ser_bmp.decode("utf-8")
                        fingerprint_code = int(decoded_bmp)   
                        break
                    if decoded_bmp == "error":
                           break
            except serial.serialutil.SerialException:
                fingerprint_code = -1
            #fingerprint_code = 10

        else:
            fingerprint_code = -1
    '''

    return fingerprint_code
def check_finger_code():
    """指紋の番号の獲得"""
    try:
        ser=serial.Serial('/dev/cu.usbmodem14301',9600)
        start_time = time.time()
        time.sleep(5)
        while True:
            ser_bmp=ser.readline()
            ser_bmp=ser_bmp.strip()
            decoded_bmp=ser_bmp.decode("utf-8")
            print(decoded_bmp)
            if decoded_bmp == "Please Type number":
                ser.write(bytes("2",'utf-8'))
            if decoded_bmp == "YourFingerID:" :
                ser_bmp=ser.readline()
                ser_bmp=ser_bmp.strip()
                decoded_bmp=ser_bmp.decode("utf-8")
                fingerprint_code = int(decoded_bmp)
                break
            if decoded_bmp == "error":
                fingerprint_code = -1
                break
            if time.time() - start_time >= 60:
                fingerprint_code = -1
                break
    except serial.serialutil.SerialException:
        fingerprint_code = -1
    return fingerprint_code

def get_finger_data(ret,choice):
    try:
        if choice == "login":
            finger_code = check_finger_code()
        if choice == "register":
            finger_code = get_finger_code()
        print(f'finger code is {finger_code}')
        if finger_code is None:
            ret['status'] = False
            ret['error'] = '指紋検測失敗1'
        if finger_code < 0:
            ret['status'] = False
            ret['error'] = '指紋検測失敗2'
        else:
            ret['status'] = True
            ret['error'] = ''
            ret['finger_code'] = str(finger_code)
    except Exception as e:
        ret['status'] = False
        # ret['error'] = '指紋検測失敗3'
        ret['error'] = str(e)
        print(f'error is {e}')
    print(f'data is {ret}')
    return ret


# /user/register
class RegisterView(View):
    """登録"""

    def get(self, request):
        """登録ページを表示"""
        fingerprint_sensor_status = con_status()
        print(fingerprint_sensor_status)
        finger_check_but_statue = request.GET.get('fingerRegister')
        finger_data = request.GET.get('fingerData')
        if finger_data is None:
            finger_data = ''
        if finger_check_but_statue is not None:
            print(f'start get~~~~~~~~~~~~')
            ret = {'status': 'True', 'error': None, 'username': request.GET.get('username'),
                   'email': request.GET.get('email'), 'finger_code': None}

            ret = get_finger_data(ret)
            print('sussecc')
            return HttpResponse(json.dumps(ret))
        return render(request, 'register.html', {'is_connect': fingerprint_sensor_status, 'finger_data': finger_data})

    def post(self, request):
        """登録処理"""
        # データを受け入れる (接受数据)
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        passwordc = request.POST.get('cpwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')
        is_finger_register = request.POST.get('fingerRegister')
        finger_name = request.POST.get('fingerData')

        # data_json = json.loads(request.body)
        data = QueryDict(request.get_full_path())
        # data = QueryDict(request.get_full_path().split('?')[1])
        # finger_name2 = data_json.get('fingerData')
        print(data)
        print(request.body)

        print(f'finger is {finger_name},finger2 is {finger_name}')
        if finger_name is None:
            finger_name = ''

        finger_password = None
        identity_types = [1]
        fingerprint_sensor_status = con_status()
        print(f'is_finger_register is {is_finger_register}.type is {type(is_finger_register)}')

        if is_finger_register == 'on':
            finger_password = name_to_psw(finger_name)
            print([is_finger_register, finger_name, finger_password, username, password, email, allow])
            # データ検証 (进行数据校验)
            if not all([finger_name, username, password, email]):
                # データが不完全 (数据不完整)

                return render(request, 'register.html',
                              {'errmsg': 'データが不完全', 'is_connect': fingerprint_sensor_status, 'fingerData': finger_name,
                               'username': username,
                               'email': email, 'allow': allow})
            identity_types.append(3)
        else:
            print([finger_name, username, password, email, allow])
            # データ検証 (进行数据校验)
            if not all([username, password, email]):
                # データが不完全 (数据不完整)

                return render(request, 'register.html',
                              {'errmsg': 'データが不完全', 'is_connect': fingerprint_sensor_status, 'fingerData': finger_name,
                               'username': username,
                               'email': email, 'allow': allow})

        # メールアドレスを検証(校验邮箱)
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html',
                          {'errmsg': 'メールアドレスのフォーマットが間違っています', 'is_connect': fingerprint_sensor_status,
                           'username': username, 'allow': allow})
        if allow != 'on':
            return render(request, 'register.html',
                          {'errmsg': 'ロボットですか？', 'is_connect': fingerprint_sensor_status, 'fingerData': finger_name,
                           'username': username,
                           'email': email, 'allow': allow})
        # ユーザの業務処理を検証します。ユーザ登録を行います。(校验用户业务处理:进行用户注册)
        try:
            user = User.objects.get(identifier=username)
        except User.DoesNotExist:
            # ユーザが存在しません (用户不存在)
            user = None
            print(f'user is none')
        if user:
            return render(request, 'register.html',
                          {'errmsg': 'ユーザ名は既に存在します', 'is_connect': fingerprint_sensor_status,
                           'finger_data': finger_name, 'email': email,
                           'allow': allow})
        try:
            check_email = UserInfo.objects.get(email=email)
        except UserInfo.DoesNotExist:
            check_email = None
            print(f'email is none')
        print(f'user is {type(user)},email is {type(check_email)}')
        if check_email:
            return render(request, 'register.html',
                          {'errmsg': 'メールは既に存在します', 'is_connect': fingerprint_sensor_status, 'fingerData': finger_name,
                           'username': username,
                           'allow': allow})

        if passwordc != password:
            return render(request, 'register.html',
                          {'errmsg': 'パスワードが一致しません', 'is_connect': fingerprint_sensor_status,
                           'fingerData': finger_name, 'username': username,
                           'email': email, 'allow': allow})

        # 業務処理 (进行业务处理)
        user = User.objects.create_user(username=username, password=password, identity_type=1,
                                        email=email, finger_name=finger_name, finger_password=finger_password)
        # user.is_active = 0
        print(f'user is {type(user)}')
        user.save()

        # アクティブなメールを送信します。リンクの有効化を含みます。http：//127.0.0.1：8000/user/active/3
        # 发送激活邮件，包含激活链接. http：//127.0.0.1：8000/user/active/3
        # リンクをアクティブにするには、ユーザの情報の識別情報が必要です。また、アイデンティティ情報を暗号化します。
        # 激活链接中需要包含用户的信息身份，并且要把身份信息进行加密
        # TODO　(完成)

        # ユーザの識別情報を暗号化して、tokenをアクティブにします。
        # 加密用户的身份信息，生成激活token
        # TODO (完成)
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'confirm': user.user_id, 'identity_types': identity_types}
        token = serializer.dumps(info)
        token = token.decode()

        # send_register_active_email.delay(email, username, token)
        # TODO　メールを送る(未完成)

        subject = '社員疲れ具合診断歓迎メッセージ'
        message = '社員疲れ具合診断'
        sender = settings.EMAIL_FROM
        receiver = [email]
        html_message = '<h1>%s,社員疲れ具合診断へようこそ</h1>リンクをクリックしてアカウントをアクティブにしてください。<br/><a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>' % (
            username, token, token)
        s = send_mail(subject, message, sender, receiver, html_message=html_message)
        print(s)

        # 応答を返して、トップページにジャンプします (返回应答,跳转到首页)
        # return render(request, 'usercent.html', {'username': username})

        # テスト用---start
        activat_message = 'http://127.0.0.1:8000/user/active/%s' % token
        return render(request, 'activat_page_test.html', {'username': username, 'activat_message': activat_message})
        # テスト用---end


class ActiveView(View):
    """アカウントをアクティブ"""

    def get(self, request, token):
        """アクティブ"""
        username = request.GET.get('username')
        # 復号を行い、アクティブにするユーザ情報を取得
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)

            # アクティブにするユーザのIDを取得
            user_id = info['confirm']
            identity_types = info['identity_types']
            with transaction.atomic():
                # IDからユーザ情報を取得
                # user = User.objects.get(id=user_id)
                userinfo = UserInfo.objects.get(id=user_id)
                userinfo.is_active = True
                userinfo.save()
                for i in identity_types:
                    user = User.objects.get(user_id=userinfo.id, identity_type=i)
                    user.is_active = userinfo.is_active
                    user.save()

            return redirect(reverse('user:login'))
        except SignatureExpired as e:
            '''リンクの有効期限が切れました'''

            return HttpResponse('リンクの有効期限が切れました')
        except Exception as e:
            print(f"error is :{e}")
            return HttpResponse(f"error is :{e}")


# /user/login
class LoginView(View):
    """ログイン (登录)"""

    def my_authenticate(self, request, username=None, password=None):
        try:
            user = User.objects.get(identifier=username)
        except Exception as e:
            user = None
        if not user:
            try:
                userinfo = UserInfo.objects.get(email=username)
                user_id = userinfo.id
                user = User.objects.get(user=user_id)
            except Exception as e:
                user = None
                print(f'user none.erro is {e}')
        if user and user.check_password(password):
            return user
        else:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def get_nickname(self, user_id):
        try:
            return UserInfo.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def get(self, request):
        """ログインページの表示"""
        identity_type = request.GET.get('identity_type')
        print(identity_type)
        username = ''
        nickname = ''
        checked = ''
        if identity_type is '1':
            # ユーザ名を覚えているかどうかを判断する
            if 'username' in request.COOKIES:
                username = request.COOKIES.get('username')
                nickname = request.COOKIES.get('nickname')
                checked = 'checked'
            # else:
            #     username = ''
            #     nickname = ''
            #     checked = ''

        elif identity_type is '2':
            pass
        elif identity_type is '3':
            time.sleep(5)
            ret = {'status': 'True', 'error': None, 'finger_code': None}
            ret = get_finger_data(ret)
            return HttpResponse(json.dumps(ret))

        # テンプレートを使う
        return render(request, 'login.html', {'username': username, 'nickname': nickname, 'checked': checked})

    def post(self, request):
        """ログイン検証"""
        # データ受信
        username = ''
        password = ''
        fingerprint_key = ''
        identity_type = request.POST.get('identity_type')

        if identity_type is '1':  # login by password
            username = request.POST.get('username')
            password = request.POST.get('pwd')
        elif identity_type is '2':
            pass
        elif identity_type is '3':  # login by fingerprint
            fingerprint_key = settings.FILE_CHARSET
            username = request.POST.get('fingerprintDataLogin')
            name_to_pw = str(username) + fingerprint_key
            password = hashlib.md5(name_to_pw.encode()).hexdigest()
        # データ検証
        if not all([username, password]):
            return render(request, 'login.html', {'errmsg': 'データが不完全'})
        print(username, password, fingerprint_key)
        finger = request.POST.get('fingerprint')
        print(f'fing is {finger}')
        # 業務処理：登録チェック
        user = self.my_authenticate(request, username=username, password=password)

        if user is not None:
            # the password verified for the user

            if user.is_active:
                # ユーザがアクティブになりました (用户已激活)
                # ユーザのログイン状態を記録します (记录用户的登录状态)
                login(request, user)
                #
                next_url = request.GET.get('next', reverse('home:index'))

                # ユーザーページに移動
                response = redirect(next_url)  # HttpResponseRedirect

                # ユーザ名を覚えておく必要があるかどうかを判断します (判断是否需要记住用户名)
                remember = request.POST.get('remember')
                if remember is None:
                    response.delete_cookie('username')
                    response.delete_cookie('nickname')
                else:
                    # 記録ユーザ名(记住用户名)
                    userinfo = UserInfo.objects.get(id=user.user_id)
                    nickname = userinfo.nickname
                    response.set_cookie('username', username, max_age=7 * 24 * 3600)
                    response.set_cookie('nickname', nickname, max_age=7 * 24 * 3600)
                # 戻る(返回)response
                return response
            else:
                print(f"user.is_active is false")
                # ユーザがアクティブではありません (用户未激活)
                return render(request, 'login.html', {'errmsg': 'ユーザがアクティブではありません'})

        else:
            # ユーザ名またはパスワードが間違っています (用户名或密码错误)
            return render(request, 'login.html', {'errmsg': 'ユーザ名またはパスワードが間違っています'})


# /user/logout
class LogoutView(View):
    """ログアウト"""

    def get(self, request):
        """ログアウト"""
        # sessionを削除
        logout(request)

        # ホームページへ
        return redirect(reverse('home:index'))


class UserInfoView(LoginRequiredMixin, View):
    """ユーザーセンター-情報"""

    def get(self, request):
        """表示"""
        # .is_authenticated()

        return render(request, 'base_haveTopBar.html', {'user'})


# TODO ユーザセンター：パスワードの変更、ユーザー情報の変更
# 測定結果の履歴、測定結果の詳細

class UserCenterView(LoginRequiredMixin, View):
    def get(self, request):
        measur_datas = MeasurementsResults.objects.filter()

        username = request.user

        return render(request, 'usercenter.html', {'measur_datas': measur_datas, 'username': username})

    def post(self, request):
        pass


class TestView(View):  # del
    def get(self, request):
        return render(request, 'test.html')
