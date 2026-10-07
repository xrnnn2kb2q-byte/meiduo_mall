from django.urls import path

from apps.goods.views import HotSKUView, ListView, SKUImageUploadView, DetailView

app_name = 'goods'

urlpatterns = [
    path('list/<int:category_id>/skus/', ListView.as_view(), name='sku_list'),
    path('hot/<int:category_id>/', HotSKUView.as_view(), name='hot_skus'),
    path('goods/<int:sku_id>/image/', SKUImageUploadView.as_view(), name='sku_image_upload'),
    path('detail/<sku_id>/', DetailView.as_view(), name='detail'),
]
