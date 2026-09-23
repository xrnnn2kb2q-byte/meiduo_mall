from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

"""
    前端
        拼接一个 url 然后给 img， img会发起请求
        url=http://ip:port/image_codes/uuid/
    
    后端
        请求              接收路由中的uuid
        业务逻辑          生成图片验证码和图片二进制，通过redis把图片验证码保存起来
        响应              返回图片二进制
        
        路由：             GET     image_codes/uuid/
        步骤：
            1.接收路由中的uuid
            2.生成图片验证码和图片二进制
            3.通过redis把图片和验证码存起来
            4.返回图片二进制
            
"""

# Create your views here.

class ImageCodeView(View):

    def get(self,reqeust,uuid):
        # 1.接收路由中的uuid
        # 2.生成图片验证码和图片二进制
        from libs.captcha.captcha import captcha
        # text是图片验证码的内容 例如：xyzz
        # image是图片二进制
        text,image = captcha.generate_captcha()

        # 3.通过redis把图片和验证码存起来
        # 3.1 进行redis的连接
        from django_redis import get_redis_connection
        redis_cli = get_redis_connection('code')
        # 3.2 指令操作
        redis_cli.setex('img_%s' % uuid,100,text)
        # 4.返回图片二进制
        # 因为图片是二进制，我们不能返回JsonResponse
        # content_type = 响应体数据类型
        # content_type的语法形式是：大类/小类
        # content_type(MIME类型)
        # 图片:image/jpeg, image/gif, image/png
        return HttpResponse(image,content_type='image/jpeg')