from django.db import models

# Create your models here.
from django.db.models import CASCADE

from users.models import Users


class Document(models.Model):
    """文件模型类"""
    status_choices = (
        (1, '待处理'),
        (2, '处理失败'),
        (3, '处理成功')
    )
    kind_choices = (
        (1, 'doc'),
        (2, 'docx'),
        (3, 'csv'),
        (4, 'txt'),
        (5, 'text'),
    )
    kind_dic = {
        'doc': 1,
        'docx': 2,
        'csv': 3,
        'txt': 4,
        'text': 5
    }
    method_choices = (
        (1, 'kenlm'),
        (2, '百度api')
    )
    method_dic = {
        'kenlm': 1,
        'baidu': 2
    }
    name = models.CharField(max_length=1024 * 3, verbose_name='文件名')
    # storage_url = models.CharField(max_length=1024 * 3, verbose_name='待纠错文件存储位置')
    user = models.ForeignKey(Users, related_name='documents', null=False, blank=False, on_delete=CASCADE,
                             verbose_name='用户')
    success_url = models.CharField(max_length=1024 * 3, default='', verbose_name='纠错完成文件存储位置')
    status = models.SmallIntegerField(choices=status_choices, default=1, verbose_name='文本处理状态')
    kind = models.SmallIntegerField(choices=kind_choices, default=1, verbose_name='文件类型')
    process_method = models.SmallIntegerField(choices=method_choices, default=1, verbose_name='处理方式')
    ct = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')
    st = models.DateTimeField(null=True, blank=True, default=None, verbose_name='处理完成时间')
