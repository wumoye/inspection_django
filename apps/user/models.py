from django.db import models
from django.contrib.auth.models import AbstractUser
from db.base_model import BaseModel


class User(AbstractUser, BaseModel):
    gender_choices = (
        (1, "男"),
        (2, "女"),
        (3, "秘密"))
    # id = models.AutoField(primary_key=True, verbose_name='ユーザーID')
    # user = models.CharField(max_length=20, blank=True, db_column='user')
    gender = models.SmallIntegerField(default=3, verbose_name="性別", choices=gender_choices, blank=True)
    # email = models.EmailField(max_length=255, blank=True)
    avatar = models.CharField(max_length=255, blank=True)
    # is_active = models.BooleanField(default=False, verbose_name='アクティブ')
    # last_login = models.DateTimeField(auto_now_add=True, verbose_name='最終ログイン時間')

    class Meta:
        db_table = 'user'
        verbose_name = 'ユーザー'
        verbose_name_plural = verbose_name


# |auths_id     |user_id		|identity_type	|identifier			|credential      |
# |1            |1  			|email			|123@example.com	|password       |
# |2            |1 			    |指紋			|           		|指紋            |
# |3            |1 			    |Google			|Google UID			|access_token   |

class Auths(BaseModel):
    identity_type_choices = (
        (1, "パスワード認証"),
        (2, "指紋認証")
    )
    auths_id = models.AutoField(primary_key=True, verbose_name='認証ID')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='ユーザーＩＤ')

    # ログインタイプ（メール、ユーザー名、指紋）またはリンク（Google、Facebook、LINEなど）
    identity_type = models.SmallIntegerField(default=1, verbose_name="認証タイプ", choices=identity_type_choices, blank=True)

    identifier = models.CharField(max_length=255, verbose_name='識別子', blank=True)

    # 認証の資格情報（サイト内にパスワードを保存し、サイト外にトークンを保存または保存しない）
    credential = models.CharField(max_length=255, verbose_name='パスワード', blank=True, )

    class Meta:
        db_table = 'auths'
        verbose_name = '認証'
        verbose_name_plural = verbose_name
