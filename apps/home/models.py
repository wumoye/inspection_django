from django.db import models
from db.base_model import BaseModel


# Create your models here.
class MeasurementResults(BaseModel):
    '''testData'''
    record_id = models.AutoField(primary_key=True, verbose_name='データ番号')
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, verbose_name='ユーザー')
    level = models.IntegerField(default=0, verbose_name='健康レベル')
    pulse = models.DecimalField(max_digits=3, decimal_places=1, verbose_name='脈拍数')

    def __str__(self):
        return self.record_id

    class Meta:
        db_table = 'records'
        verbose_name = '測定結果'
        verbose_name_plural = verbose_name

