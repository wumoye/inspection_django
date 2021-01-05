from django.db import models, transaction
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, PermissionsMixin, BaseUserManager
from db.base_model import BaseModel


class UserInfo(BaseModel):
    GENDER_TYPE = (
        (1, "男"),
        (2, "女"),
        (3, "秘密")
    )
    id = models.AutoField(primary_key=True, verbose_name='ユーザーID')
    nickname = models.CharField(max_length=13, verbose_name="昵称", null=True, blank=True)
    email = models.EmailField(verbose_name="メールアドレス", unique=True)
    age = models.IntegerField(verbose_name="年齢", null=True, blank=True)
    gender = models.CharField(max_length=2, choices=GENDER_TYPE, verbose_name="性別", null=True, blank=True)
    avatar = models.ImageField(upload_to="Store/user_picture", verbose_name="用户头像", null=True, blank=True)
    is_active = models.BooleanField(default=False, verbose_name="激活状态")

    class Meta:
        db_table = 'my_user_info'
        verbose_name = "ユーザー情報"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.id


class UserManager(BaseUserManager):
    def _create_user(self, username, password, identity_type, email, **kwargs):
        # if not identity_type:
        #     raise ValueError("ログイン方法を選択してください！")

        if not username:
            raise ValueError("ユーザー名を入力してください！")
        if not password:
            raise ValueError("パスワードを入力してください！")
        if not email:
            raise ValueError("メールアドレスを入力してください！")
        try:
            with transaction.atomic():
                userinfo = UserInfo(nickname=username, email=email)
                userinfo.save()
                user_id = UserInfo.objects.get(id=userinfo.id)
                user = User(user=user_id, identity_type=identity_type, identifier=username, **kwargs)
                user.set_password(password)
                user.is_active = userinfo.is_active

                user.save()
                return user
        except Exception as e:
            print(f"error is :{e}")

    def create_user(self, username, password, identity_type, email, **kwargs):
        kwargs['is_superuser'] = False
        return self._create_user(username, password, identity_type, email, **kwargs)

    def create_superuser(self, username, password, identity_type, email, **kwargs):
        kwargs['is_superuser'] = True
        kwargs['is_staff'] = True
        return self._create_user(username, password, identity_type, email, **kwargs)


# |auths_id     |user_id		|identity_type	|identifier			|password      |
# |1            |1  			|username		|lee            	|password       |
# |2            |1  			|email			|123@example.com	|password       |
# |3            |1 			    |指紋			|           		|指紋            |
# |4            |1 			    |Google			|Google UID			|access_token   |

class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    """user_auths"""
    identity_type_choices = (
        (1, "ユーザー名とパスワード認証"),
        (2, "メールとパスワード認証"),
        (3, "指紋認証")
    )
    id = models.AutoField(primary_key=True, verbose_name='認証ID')
    user = models.ForeignKey(UserInfo, on_delete=models.CASCADE, max_length=50, verbose_name="ユーザー")
    # ログインタイプ（メール、ユーザー名、指紋）またはリンク（Google、Facebook、LINEなど）
    identity_type = models.SmallIntegerField(default=1, verbose_name="認証タイプ", choices=identity_type_choices, blank=True)
    identifier = models.CharField(max_length=255, verbose_name='識別子', unique=True)
    is_active = models.BooleanField(default=False, verbose_name="激活状态")

    USERNAME_FIELD = 'identifier'
    # REQUIRED_FIELDS = ['email']
    # EMAIL_FIELD = 'email'

    objects = UserManager()

    class Meta:
        db_table = 'my_auths'
        verbose_name = "認証"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.id
