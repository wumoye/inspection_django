from django.db import models
from django.contrib.auth.models import AbstractUser
from db.base_model import BaseModel


# Create your models here.

class User(AbstractUser, BaseModel):
    '''用户模型类'''

    class Meta:
        db_table = 'df_user'
        verbose_name = 'ユーザー'
        verbose_name_plural = verbose_name


class MeasurementResults(BaseModel):
    '''testData'''
    data_id = models.AutoField(primary_key=True, verbose_name='データ番号')
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, verbose_name='ユーザー')

    pulse = models.DecimalField(max_digits=4, decimal_places=1, verbose_name='脈拍数')
    level = models.IntegerField(default=0, verbose_name='健康レベル')

    def __str__(self):
        return self.data_id

    class Meta:
        db_table = 'df_measurement_results'
        verbose_name = '測定結果'
        verbose_name_plural = verbose_name
