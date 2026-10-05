from django.urls import path

from apps.goods.views import SKUImageUploadView

app_name = 'goods'

urlpatterns = [
    path('goods/<int:sku_id>/image/', SKUImageUploadView.as_view(), name='sku_image_upload'),
]
