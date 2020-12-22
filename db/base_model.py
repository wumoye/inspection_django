from django.db import models


class BaseModel(models.Model):
    '''モデル抽象ベース'''

    class Meta:
        abstract = True

    create_time = models.DateTimeField(auto_now_add=True, verbose_name='作成時間')
    update_time = models.DateTimeField(auto_now_add=True, verbose_name='更新時間')
    is_delete = models.BooleanField(default=False, verbose_name='削除タグ')
