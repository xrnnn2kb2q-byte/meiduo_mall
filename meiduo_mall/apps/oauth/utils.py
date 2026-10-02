from itsdangerous import URLSafeSerializer as Serializer
from django.conf import settings

# 加密
def generic_openid(openid):
    s = Serializer(secret_key=settings.SECRET_KEY)
    access_token = s.dumps({'openid':openid})

    # 将bytes类型的数据转换为 str
    return access_token.decode()

# 解密
def check_openid(token):
    s = Serializer(secret_key=settings.SECRET_KEY)
    try:
        result = s.loads(token)
    except Exception:
        return None
    else:
        return result.get('openid')