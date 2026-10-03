from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from apps.areas.models import Area

# Create your views here.

"""
需求：
    获取省份信息
    
前端：
    当页面加载的时候，会发送axios请求，来获取 省份信息

后端：
    请求：         不需要请求参数
    业务逻辑：      查询省份信息
    响应：         JSON
    路由：         areas/
    步骤：
        1.查询省份信息
        2.将对象转换为字典数据
        3.返回响应
"""

class AreasView(View):
    def get(self, request):
        # 1.查询省份信息
        provinces = Area.objects.filter(parent=None)
        # 查询结果集
        # 2.将对象转换为字典数据
        province_list = []
        for province in provinces:
            province_list.append({
                'id':province.id,
                'name':province.name,
            })
        # 3.返回响应
        return JsonResponse({'code':0,'errmsg':'ok','province_list':province_list})