"""
URL configuration for meiduo_mall project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include


# def log(request):
#     # 1. 导入
#     import logging
#     # 2. 创建日志器
#     logger = logging.getLogger('django')
#     # 3. 调用日志器的方法来保存信息
#     logger.info('用户登录了')
#     logger.warning('redis缓存不足')
#     logger.error('该记录不存在')
#     logger.debug('~~~~~~~~~~~~~~~')
#
#     return HttpResponse('log')

# 注册转换器
from utils.converters import UsernameConverter
from django.urls import register_converter, include

register_converter(UsernameConverter, 'username_converter')

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('log/',log),
    # 导入 users子应用的路由
    path('',include('apps.users.urls')),
    path('',include('apps.verifications.urls')),
]
