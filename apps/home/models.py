from django.db import models
from db.base_model import BaseModel


# Create your models here.
class MeasurementsResults(BaseModel):
    """diagnosis"""
    record_id = models.AutoField(primary_key=True, verbose_name='データ番号')
    user = models.ForeignKey('user.UserInfo', on_delete=models.CASCADE, verbose_name='ユーザー')
    level = models.IntegerField(default=0, verbose_name='健康レベル')
    pulse = models.DecimalField(max_digits=4, decimal_places=1, verbose_name='脈拍数')

    def __str__(self):
        return self.record_id

    class Meta:
        db_table = 'my_records'
        verbose_name = '測定結果'
        verbose_name_plural = verbose_name

