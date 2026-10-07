from django.urls import path, re_path

from apps.goods.views import DetailView, HotSKUView, ListView, LocalGoodsImageView, SKUImageUploadView

app_name = 'goods'

urlpatterns = [
    path('list/<int:category_id>/skus/', ListView.as_view(), name='sku_list'),
    path('hot/<int:category_id>/', HotSKUView.as_view(), name='hot_skus'),
    path('goods/<int:sku_id>/image/', SKUImageUploadView.as_view(), name='sku_image_upload'),
    path('goods/images/<str:image_name>', LocalGoodsImageView.as_view(), name='local_goods_image'),
    path('detail/<int:sku_id>/', DetailView.as_view(), name='detail'),
    re_path(r'^goods/(?P<sku_id>[0-9]+)\.html$', DetailView.as_view(), name='detail_legacy'),
]
