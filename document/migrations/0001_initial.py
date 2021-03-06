# Generated by Django 2.1.3 on 2020-06-11 07:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=3072, verbose_name='文件名')),
                ('storage_url', models.CharField(max_length=3072, verbose_name='待纠错文件存储位置')),
                ('success_url', models.CharField(max_length=3072, verbose_name='纠错完成文件存储位置')),
                ('status', models.SmallIntegerField(choices=[(1, '待处理'), (2, '处理失败'), (3, '处理成功')], default=1, verbose_name='文本处理状态')),
                ('ct', models.DateTimeField(auto_now_add=True, verbose_name='上传时间')),
                ('st', models.DateTimeField(blank=True, default=None, null=True, verbose_name='处理完成时间')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
        ),
    ]
