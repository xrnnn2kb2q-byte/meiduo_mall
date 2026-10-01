from django.shortcuts import render

# Create your views here.

"""
第三方登录的步骤：
    1.QQ互联开发平台中申请成为开发者（可以不用做）
    2.QQ互联创建应用（可以不用做）
    3.按照文件开发（看文档的）

    3.1.准备工作：                                          -------------准备好了
        # QQ登录参数
        # 我们申请的 客户端id
        QQ_CLIENT_ID = '101474184'          appid
        # 我们申请的 客户端秘钥
        QQ_CLIENT_SECRET = 'c6ce949e04e12ecc909ae6a8b09b637c'           appkey
        # 我们申请时添加的: 登录成功后回调的路径
        QQ_REDIRECT_URI = 'http://www.meiduo.site:8080/oauth_callback.html'
    3.2.放置 QQ登录的图标（目的：让我们点击QQ图标来实现第三方登录） -----------前端做好了
    3.3.根据oauth2.0 来获取code 和 token                      ----------我们要做的
        对于应用而言，需要进行两步
        1.获取Authorization Code；         表面是一个连接，实质是需要用户同意，然后获取code
        2.通过Authorization Code 获取 Access Token
    3.4.通过token换取 openid                                ------------我们要做的
        openid是此网站上唯一对应用户身份的标识，网站可将此ID进行存储便于用户下次登陆时辨识其身份，或将其与用户在网站上的原有账号进行绑定

1.生成用户绑定链接 ----> 2.获取code --------->3.获取token ------------>4.获取openid -------------> 5.保存openid

"""


"""
生成用户绑定链接

前端：当用户点击QQ登录图标的时候，前端应该发送一个axios（Ajax）请求

后端：
    请求                  
    业务逻辑                调用QQLoginTool 生成跳转链接
    响应                   返回跳转链接{'code':0,'qq_login_url':'http://xxx'}
    路由                   GET
    步骤
        1.生成 QQLoginTool 实例对象
        2.调用对象的方法生成跳转链接
        3.返回响应

404: 路由不匹配
405: 方法不被允许（你没有实现请求对应的方法）

"""
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from meiduo_mall import settings
from django.http import JsonResponse

class QQLoginURLView(View):
    def get(self,request):
        # 1.生成 QQLoginTool 实例对象
        # client_id = None              appid
        # client_secret = None          appsecret
        # redirect_uri = None           用户同意登录之后，跳转的页面
        # state = None                  不知道什么意思，随便写，等出了问题再分析问题
        qq = OAuthQQ(
            client_id = settings.QQ_CLIENT_ID,
            client_secret = settings.QQ_CLIENT_SECRET,
            redirect_uri = settings.QQ_REDIRECT_URI,
            state = 'xxx',
        )
        # 2.调用对象的方法生成跳转链接
        qq_login_url = qq.get_qq_url()
        # 3.返回响应
        return JsonResponse({'code':0,'errmsg':'ok','login_url':qq_login_url})

"""
    需求：获取code，通过code获取token，再通过token获取openid
    
    前端：
        应该获取 用户同意登录的code，把这个code发送给后端
    后端：
        请求          获取code
        业务逻辑       通过code换取token，再通过token获取openid
                      根据openid进行判断
                      如果没有绑定过，则需要绑定
                      如果绑定过，则直接登录
        响应           
        路由          GET         oauth_callback/code=xxxxxxxx
        步骤
            1.获取code
            2.通过code换取token
            3.再通过token获取openid
            4.根据openid进行判断
            5.如果没有绑定过，则需要绑定
            6.如果绑定过，则直接登录
"""
from apps.oauth.models import OAuthQQUser
from django.contrib.auth import login
class OauthQQView(View):
    def get(self,request):
        code = request.GET.get('code')
        if code is None:
            return JsonResponse({'code':400,'errmsg':'参数不全'})
        qq = OAuthQQ(
            client_id=settings.QQ_CLIENT_ID,
            client_secret=settings.QQ_CLIENT_SECRET,
            redirect_uri=settings.QQ_REDIRECT_URI,
            state='xxx',
        )
        token = qq.get_access_token(code)
        openid = qq.get_open_id(token)
        try:
            qquser = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 不存在
            response = JsonResponse({'code':400,'access_token':openid})
            return response
        else:
            # 存在
            # 6.1 设置session
            login(request, qquser.user)
            # 6.2 设置cookie
            response = JsonResponse({'code':0,'errmsg':'ok'})
            response.set_cookie('username',qquser.user.username)
            return response
