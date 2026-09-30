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

1.生成用户绑定链接 ----> 获取code --------->获取token ------------>获取openid -------------> 保存openid
"""