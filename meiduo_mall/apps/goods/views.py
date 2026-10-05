from django.shortcuts import render
from django import forms
from django.http import JsonResponse
from django.views import View

from apps.goods.models import SKU
from utils.views import LoginRequiredJSONMixin

# Create your views here.

"""
关于模型的分析
1.根据页面效果 尽量多的分析字段
2.去分析是保存在一个表中 还是多个表中（多举例说明）

分析表的关系的时候 最多不要超过3个表

学生 和 老师

学生表
stu_id      stu_name

老师表
teacher_id  teacher_name
666            牛老师
999            齐老师

第三张表
stu_id      teacher_id
100             666
100             999
200             666
200             999

商品day01      模型的分析 --> Fdfs(用于保存图片、视频的那个文件) --> 为了部署Fdfs学习Docker

"""


class SKUImageUploadView(LoginRequiredJSONMixin, View):
    """Upload and set the default image for an existing SKU."""

    max_image_size = 5 * 1024 * 1024  # 5 MiB

    def post(self, request, sku_id):
        if not request.user.is_staff:
            return JsonResponse({'code': 403, 'errmsg': '没有商品图片上传权限'}, status=403)

        try:
            sku = SKU.objects.get(pk=sku_id)
        except SKU.DoesNotExist:
            return JsonResponse({'code': 404, 'errmsg': '商品 SKU 不存在'}, status=404)

        image = request.FILES.get('image')
        if image is None:
            return JsonResponse({'code': 400, 'errmsg': '请通过 image 字段上传图片'}, status=400)
        if image.size > self.max_image_size:
            return JsonResponse({'code': 400, 'errmsg': '图片不能超过 5 MB'}, status=400)

        try:
            # ImageField validation checks that the uploaded content is a real image.
            image = forms.ImageField().clean(image)
        except forms.ValidationError:
            return JsonResponse({'code': 400, 'errmsg': '上传文件不是有效图片'}, status=400)

        sku.default_image = image
        sku.save(update_fields=['default_image'])

        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'sku_id': sku.id,
            'image': sku.default_image.url,
        })
