from types import SimpleNamespace

from django.test import SimpleTestCase
from django.template.loader import get_template
from django.urls import resolve

from apps.goods.views import DetailView, _sku_fallback_image_url


class LocalGoodsImageTests(SimpleTestCase):
    def test_sku_fallback_points_to_backend_local_image_route(self):
        sku = SimpleNamespace(
            id=14,
            name='Apple iPhone 8 Plus',
            category=SimpleNamespace(name='手机', parent=None),
        )

        image_url = _sku_fallback_image_url(sku)

        self.assertTrue(image_url.endswith('/goods/images/goods004.jpg'))

    def test_legacy_goods_detail_url_resolves_to_detail_view(self):
        match = resolve('/goods/14.html')

        self.assertIs(match.func.view_class, DetailView)
        self.assertEqual(match.kwargs, {'sku_id': '14'})

    def test_local_goods_image_route_serves_jpeg(self):
        response = self.client.get('/goods/images/goods008.jpg')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/jpeg')
        image_bytes = b''.join(response.streaming_content)
        self.assertTrue(image_bytes.startswith(b'\xff\xd8'))

    def test_local_goods_image_route_rejects_unknown_filename(self):
        response = self.client.get('/goods/images/not-an-image.jpg')

        self.assertEqual(response.status_code, 404)

    def test_detail_template_renders_the_backend_image_url(self):
        template = get_template('detail.html')
        html = template.render({
            'frontend_url': 'http://frontend.test:8080',
            'sku_image_url': 'http://backend.test:8000/goods/images/goods008.jpg',
            'sku_fallback_image_url': 'http://backend.test:8000/goods/images/goods008.jpg',
            'categories': {},
            'breadcrumb': {},
            'specs': [],
            'hot_skus': [],
            'sku': type('SKUStub', (), {
                'name': 'Local image test product',
                'caption': '',
                'price': '12.00',
                'market_price': '15.00',
                'comments': 0,
                'stock': 1,
                'sales': 0,
                'spu': type('SPUStub', (), {
                    'desc_detail': '',
                    'desc_pack': '',
                    'desc_service': '',
                })(),
            })(),
        })

        self.assertIn('src="http://backend.test:8000/goods/images/goods008.jpg"', html)
