from django.utils.http import urlquote
from django.http import JsonResponse, StreamingHttpResponse, QueryDict
from django.shortcuts import render
import os, base64
from document.models import Document
from document.tasks import process_file
from utils.libs import file_iterator


# Create your views here.

def index(request):
    if request.method == 'GET':
        return render(request, 'document/index.html')


def upload_correction(request):
    # 文件上传显示
    if request.method == 'GET':
        files = Document.objects.filter(user=request.user).order_by('-ct')
        return render(request, 'document/file_correction.html', locals())

    if request.method == 'POST':
        """上传文件纠错"""
        file = request.FILES.get('file')
        method = request.POST.get('method')
        if not file:
            return JsonResponse({'code': 400, 'msg': '未获取到文件!'})
        if file.size > 1024 * 1024 * 10:
            return JsonResponse({'code': 400, 'msg': '上传文件不能大于10M!'})
        file_type = file.name.split(r'.')[-1].lower()
        if file_type not in Document.kind_dic.keys() or method not in Document.method_dic.keys():
            return JsonResponse({'code': 400, 'msg': f'暂时只支持{Document.kind_dic.keys()}类型文件!'})
        doc = Document.objects.create(name=file.name, user=request.user, kind=Document.kind_dic[file_type],
                                      process_method=Document.method_dic[method])
        file_bytes = file.file.read()
        b64_str = base64.b64encode(file_bytes).decode()
        with open(f'{doc.pk}_{file.name}', 'wb') as f:
            f.write(file_bytes)
        process_file.delay(file_type, b64_str, f'{doc.pk}_{file.name}', request.user.username, doc.pk, method)

        return JsonResponse({'code': 200, 'msg': '成功,请耐心等待处理!'})

    if request.method == 'DELETE':
        data = QueryDict(request.body)
        f_id = data.get('id')
        Document.objects.filter(user=request.user, id=f_id).delete()
        return JsonResponse({'code': 200, 'msg': '删除成功!'})


def download(request):
    """下载文件"""
    if request.method == 'GET':
        f_id = request.GET.get('id')
        f = Document.objects.filter(id=f_id, user=request.user).first()
        if not f:
            return JsonResponse({'code': 400, 'msg': '文件不存在!'})
        if f.status != 3:
            return JsonResponse({'code': 400, 'msg': '文件未处理完!'})
        if not os.path.exists(f.success_url):
            return JsonResponse({'code': 400, 'msg': '文件不存在!'})
        file_name = f.name
        if f.kind == 1:
            file_name = f.name[:-4] + '.docx'
        resp = StreamingHttpResponse(file_iterator(f.success_url))
        resp['Content-Type'] = 'application/octet-stream'
        resp['Content-Disposition'] = f'attachment;filename={urlquote(file_name)}'
        return resp
