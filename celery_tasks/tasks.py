# 使用celery
from django.core.mail import send_mail
from django.conf import settings
from celery import Celery

import time

# django環境初期化
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dailyfresh.settings')
django.setup()

# Cleryクラスのインスタンスオブジェクトを作成
app = Celery('celery_tasks', broker='redis://127.0.0.1:6379/6')


# 定義タスク関数
@app.task
def send_register_active_email(to_email, username, token):
    '''メールを送る'''

    subject = '社員疲れ具合診断歓迎メッセージ'
    message = '社員疲れ具合診断'
    sender = settings.EMAIL_FROM
    receiver = [to_email]
    html_message = '<h1>%s,会員登録を歓迎します</h1>リンクをクリックしてアカウントをアクティブにしてください。<br/><a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>' % (
        username, token, token)
    print(html_message)
    s = send_mail(subject, message, sender, receiver, html_message=html_message)
    print(s)

