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

"""
1.注册
我们提供免费开发测试，【免费开发测试前，请先 注册 成为平台用户】。咨询在线客服


2.绑定测试号
免费开发测试需要在"控制台—管理—号码管理—测试号码"绑定 测试号码 。

3.开发测试
开发测试过程请参考 短信业务接口 及 Demo示例 / sdk参考（新版）示例。Java环境安装请参考"新版sdk"。

4.免费开发测试注意事项
    4.1.免费开发测试需要使用到"控制台首页"，开发者主账户相关信息，如主账号、应用ID等。

    4.2.免费开发测试使用的模板ID为1，具体内容：【云通讯】您的验证码是{1}，请于{2}分钟内正确输入。其中{1}和{2}为短信模板参数。

    4.3.测试成功后，即可申请短信模板并 正式使用 。
"""