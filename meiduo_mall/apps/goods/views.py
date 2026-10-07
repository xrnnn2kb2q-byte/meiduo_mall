from django.shortcuts import render
from django import forms
from django.conf import settings
from django.core.files.storage import default_storage
import mimetypes
from pathlib import Path

from django.http import FileResponse, Http404, JsonResponse
from django.views import View

from apps.goods.models import GoodsChannel, SKU, SKUSpecification, GoodsCategory
from utils.views import LoginRequiredJSONMixin


def get_bread_crump(category):
    """Build the category path used by the list and detail page breadcrumbs."""
    ancestors = []
    parent = category.parent
    while parent:
        ancestors.append(parent)
        parent = parent.parent
    category_path = (list(reversed(ancestors)) + [category])[:3]

    breadcrumb = {}
    for index, key in enumerate(('cat1', 'cat2', 'cat3')):
        if index < len(category_path):
            item = category_path[index]
            breadcrumb[key] = item.name
            breadcrumb[f'{key}_url'] = f'/list.html?cat={item.id}'
        else:
            breadcrumb[key] = ''
            breadcrumb[f'{key}_url'] = ''
    return breadcrumb


def get_categories():
    """Build the navigation structure expected by the category menu template."""
    categories = {}
    channels = GoodsChannel.objects.select_related(
        'group', 'category'
    ).order_by('group_id', 'sequence')

    for channel in channels:
        group = categories.setdefault(channel.group_id, {
            'channels': [],
            'sub_cats': [],
        })
        group['channels'].append({
            'name': channel.category.name,
            'url': channel.url,
        })
        group['sub_cats'].extend([
            {
                'id': category.id,
                'name': category.name,
                'sub_cats': category.subs.all(),
            }
            for category in channel.category.subs.prefetch_related('subs')
        ])
    return categories


def get_goods_specs(sku):
    """Return specification options and their SKU links for a detail page."""
    result = []
    specs = sku.spu.specs.prefetch_related('options').all()
    for spec in specs:
        sku_by_option = {}
        links = SKUSpecification.objects.filter(
            spec=spec,
            sku__spu=sku.spu,
        ).order_by('sku_id').values_list('option_id', 'sku_id')
        for option_id, sku_id in links:
            sku_by_option.setdefault(option_id, sku_id)
        current_option_id = SKUSpecification.objects.filter(
            sku=sku,
            spec=spec,
        ).values_list('option_id', flat=True).first()
        if current_option_id is not None:
            sku_by_option[current_option_id] = sku.id

        result.append({
            'name': spec.name,
            'spec_options': [
                {
                    'value': option.value,
                    'sku_id': sku_by_option.get(option.id),
                }
                for option in spec.options.all()
            ],
        })
    return result


def _sku_fallback_image_url(sku):
    """Use a product-family fallback from the frontend's local image assets."""
    product_text = sku.name.casefold()
    category = sku.category
    category_names = []
    while category:
        category_names.append(category.name.casefold())
        category = category.parent
    product_text += ' ' + ' '.join(category_names)

    if any(word in product_text for word in ('抽纸', '纸巾', '面巾纸', '卫生纸')):
        image_name = 'fallback_009.jpg'
    elif any(word in product_text for word in ('路由器', '路由', 'router')):
        image_name = 'fallback_007.jpg'
    elif any(word in product_text for word in ('笔记本', '电脑', 'macbook', 'laptop')):
        image_name = 'fallback_008.jpg'
    elif any(word in product_text for word in ('平板', 'ipad', 'tablet')):
        image_name = 'fallback_006.jpg'
    elif any(word in product_text for word in ('手机', 'iphone', 'huawei', '华为', 'apple')):
        # Local files 001–005 are phone product photos. Vary them by SKU so
        # the hot ranking does not repeat the exact same thumbnail.
        image_name = f'fallback_{(sku.id - 1) % 5 + 1:03d}.jpg'
    else:
        image_name = 'no_image.svg'

    if image_name.startswith('fallback_'):
        image_name = image_name.replace('fallback_', 'goods', 1)
    return f'{settings.BACKEND_URL}/goods/images/{image_name}'


def _sku_image_url(sku):
    """Prefer the uploaded local image; otherwise use a local fallback asset."""
    image = sku.default_image
    if image and default_storage.exists(image.name):
        return f'{settings.BACKEND_URL}/{image.url.lstrip("/")}'
    return _sku_fallback_image_url(sku)


class LocalGoodsImageView(View):
    """Serve the project's bundled product images from the Django host."""

    allowed_images = {f'goods{number:03d}.jpg' for number in range(1, 10)} | {'no_image.svg'}

    def get(self, request, image_name):
        if image_name not in self.allowed_images:
            raise Http404('商品图片不存在')

        image_path = settings.BASE_DIR.parent / 'front_end_pc' / 'images' / 'goods' / image_name
        if not image_path.is_file():
            raise Http404('商品图片不存在')

        content_type, _ = mimetypes.guess_type(image_path.name)
        return FileResponse(image_path.open('rb'), content_type=content_type or 'application/octet-stream')

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

class ListView(View):
    def get(self, request, category_id):
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return JsonResponse({'code': 404, 'errmsg': '商品类别不存在'}, status=404)

        ordering = request.GET.get('ordering', '-create_time')
        if ordering not in {'-create_time', 'price', '-sales'}:
            ordering = '-create_time'
        try:
            page_size = min(max(int(request.GET.get('page_size', 5)), 1), 100)
            page = max(int(request.GET.get('page', 1)), 1)
        except (TypeError, ValueError):
            return JsonResponse({'code': 400, 'errmsg': '分页参数无效'}, status=400)

        skus = SKU.objects.filter(category_id=category_id).order_by(ordering, '-id')
        from django.core.paginator import Paginator, EmptyPage
        paginator = Paginator(skus, page_size)
        try:
            page_skus = paginator.page(page)
        except EmptyPage:
            page_skus = paginator.page(paginator.num_pages or 1)

        sku_list = []
        for sku in page_skus.object_list:
            sku_list.append({
                'id': sku.id,
                'name': sku.name,
                'price': str(sku.price),
                'comments': sku.comments,
                'default_image_url': _sku_image_url(sku),
            })

        breadcrumb = get_bread_crump(category)

        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'list': sku_list,
            'count': paginator.num_pages,
            'breadcrumb': breadcrumb,
        })


class HotSKUView(View):
    """Return the top selling SKUs in a category for the list page."""

    def get(self, request, category_id):
        if not GoodsCategory.objects.filter(pk=category_id).exists():
            return JsonResponse({'code': 404, 'errmsg': '商品类别不存在'}, status=404)

        hot_skus = SKU.objects.filter(category_id=category_id).order_by('-sales', '-id')[:5]
        results = []
        for sku in hot_skus:
            results.append({
                'id': sku.id,
                'name': sku.name,
                'price': str(sku.price),
                'sales': sku.sales,
                'default_image_url': _sku_image_url(sku),
            })

        return JsonResponse({'code': 0, 'errmsg': 'ok', 'hot_skus': results})

"""
搜索：

1.我们不使用like

2.我们使用 全文检索
    全文检索即在指定的任意字段中进行检索查询
    
3.全文检索方案需要配合搜索引擎来实现

4.搜索引擎
    原理：关键词与词条的对应关系，并记录词条的位置。

1. --- 我爱北京天安门                      我爱，北京，天安门

2. --- 王红，我爱你，我想你想的睡不着觉       王红，我爱，我爱你，睡不着觉，想你

3. ---我睡不着觉                          我，睡不着觉

    我爱
    
5.Elasticsearch
    进行分词操作
    分词是指将一句话插接成多个单字或词，这些字或词便是这句话的关键词
    
    下雨天 留客天 天留我不留

"""

"""
需求：
    详情页面
    
    1.分类数据
    2.面包屑
    3.SKU信息
    4.规格信息

    我们的详情页面也是需要静态化实现的，但是我们在讲解静态化之前，应该可以先把 详情页面的数据展示出来
"""

class DetailView(View):
    def get(self, request, sku_id):
        try:
            sku = SKU.objects.select_related(
                'spu', 'category__parent__parent'
            ).get(id=sku_id)
        except SKU.DoesNotExist:
            raise Http404('商品不存在')

        hot_skus = SKU.objects.filter(category=sku.category).exclude(
            pk=sku.pk
        ).order_by('-sales', '-id')[:5]
        for hot_sku in hot_skus:
            hot_sku.image_url = _sku_image_url(hot_sku)
            hot_sku.fallback_image_url = _sku_fallback_image_url(hot_sku)

        context = {
            'categories': get_categories(),
            'breadcrumb': get_bread_crump(sku.category),
            'frontend_url': settings.FRONTEND_URL,
            'sku': sku,
            'sku_image_url': _sku_image_url(sku),
            'sku_fallback_image_url': _sku_fallback_image_url(sku),
            'specs': get_goods_specs(sku),
            'hot_skus': hot_skus,
        }
        return render(request, 'detail.html', context)
