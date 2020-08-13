from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.views.generic import View
from user.models import User
import re


# Create your views here.

class RegisterView(View):
    '''登録 (注册)'''

    def get(self, request):
        '''登録ページを表示 (显示注册页面)'''
        return render(request, 'register.html')

    def post(self, request):
        '''登録処理 (进行注册处理)'''
        # データを受け入れる (接受数据)
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        passwordc = request.POST.get('cpwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')

        print([username, password, email,allow])
        # データ検証 (进行数据校验)
        if not all([username, password, email]):
            # データが不完全 (数据不完整)
            return render(request, 'register.html', {'errmsg': 'データが不完全'})
        # メールアドレスを検証(校验邮箱)
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': 'メールアドレスのフォーマットが間違っています'})

        # ユーザの業務処理を検証します。ユーザ登録を行います。(校验用户业务处理:进行用户注册)
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # ユーザ名が存在しません (用户名不存在)
            user = None
        if user:
            return render(request, 'register.html', {'errmsg': 'ユーザ名は既に存在します'})

        if passwordc != password:
            return render(request, 'register.html', {'errmsg': 'パスワードが一致しません'})

        # 業務処理 (进行业务处理)
        user = User.objects.create_user(username, email, password)

        # user.is_active = 0
        if allow == 'on':
            user.is_active = 1
        else:
            user.is_active = 0
        print(user.is_active)
        user.save()

        # TODO
        # アクティブなメールを送信します。リンクの有効化を含みます。http：//127.0.0.1：8000/user/active/3
        # 发送激活邮件，包含激活链接. http：//127.0.0.1：8000/user/active/3
        # リンクをアクティブにするには、ユーザの情報の識別情報が必要です。また、アイデンティティ情報を暗号化します。
        # 激活链接中需要包含用户的信息身份，并且要把身份信息进行加密

        # TODO
        # ユーザの識別情報を暗号化して、tokenをアクティブにします。
        # 加密用户的身份信息，生成激活token

        # TODO
        # メールを送る

        # 応答を返して、トップページにジャンプします (返回应答,跳转到首页)
        return render(request, 'mypage.html', {'username': username})


# /user/login
class LoginView(View):
    '''ログイン (登录)'''

    def get(self, request):
        '''ログインページを表示 (显示登录页面)'''
        # TODO
        #  ユーザ名を覚えているかどうかを判断します (判断是否记住了用户名)

        # テンプレートを使う (使用模板)
        return render(request, 'login.html')

    def post(self, request):
        '''ログイン検証 (登录校验)'''
        # データ受信(接收数据)
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        test = request.POST.get('remember')

        if test is not None:
            checked = ''
            return render(request, 'mypage.html', {'username': username, 'password': password, 'checked': checked})

        # データ検証 (校验数据)
        if not all([username, password]):
            return render(request, 'login.html', {'errmsg': 'データが不完全'})

        # 業務処理：登録チェック (业务处理：登录校验)
        user = authenticate(username=username, password=password)
        print(user)
        if user is not None:
            # the password verified for the user
            if user.is_active:
                # ユーザがアクティブになりました (用户已激活)
                # ユーザのログイン状態を記録します (记录用户的登录状态)
                login(request, user)

                # トップページに移動 (跳转到首页)
                print(user)
                response = render(request, 'mypage.html')
                # TODO
                # ユーザ名を覚えておく必要があるかどうかを判断します (判断是否需要记住用户名)
                # 記録ユーザ名(记住用户名)
                # 戻る(返回)response
                return response
            else:
                print(user)
                # ユーザがアクティブではありません (用户未激活)
                return render(request, 'login.html', {'errmsg': 'ユーザがアクティブではありません'})

        else:
            # ユーザ名またはパスワードが間違っています (用户名或密码错误)
            return render(request, 'login.html', {'errmsg': 'ユーザ名またはパスワードが間違っています'})
