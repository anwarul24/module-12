from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import Product

URL = '/api/products/'
VALID = {'name': 'Notebook', 'description': 'A notebook with 100 pages.',
         'price': '120.00', 'stock': 25}


class ProductAPITests(APITestCase):
    def setUp(self):
        user = get_user_model().objects.create_user('tester', password='pw12345!')
        self.token = Token.objects.create(user=user)

    def auth(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_list_public_and_empty(self):
        r = self.client.get(URL)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['results'], [])
        self.assertEqual(r.data['count'], 0)

    def test_create_with_token(self):
        self.auth()
        r = self.client.post(URL, VALID, format='json')
        self.assertEqual(r.status_code, 201)
        self.assertIn('id', r.data)
        self.assertEqual(Product.objects.count(), 1)

    def test_create_without_token_denied(self):
        r = self.client.post(URL, VALID, format='json')
        self.assertEqual(r.status_code, 401)
        self.assertEqual(Product.objects.count(), 0)

    def test_invalid_token_denied(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token wrong')
        self.assertEqual(self.client.post(URL, VALID, format='json').status_code, 401)

    def test_empty_name(self):
        self.auth()
        for name in ['', '   ']:
            r = self.client.post(URL, {**VALID, 'name': name}, format='json')
            self.assertEqual(r.status_code, 400)
            self.assertIn('name', r.data)

    def test_price_zero_or_negative(self):
        self.auth()
        for price in ['0', '0.00', '-5.00']:
            r = self.client.post(URL, {**VALID, 'price': price}, format='json')
            self.assertEqual(r.status_code, 400, price)
            self.assertIn('price', r.data)

    def test_negative_and_fractional_stock(self):
        self.auth()
        for stock in [-1, 2.5, 'abc']:
            r = self.client.post(URL, {**VALID, 'stock': stock}, format='json')
            self.assertEqual(r.status_code, 400, stock)
            self.assertIn('stock', r.data)

    def test_client_cannot_set_id(self):
        self.auth()
        r = self.client.post(URL, {**VALID, 'id': 999}, format='json')
        self.assertEqual(r.status_code, 201)
        self.assertNotEqual(r.data['id'], 999)

    def test_ordering_and_second_page(self):
        self.auth()
        for i in range(1, 7):
            self.client.post(URL, {**VALID, 'name': f'Item {i}'}, format='json')
        self.client.credentials()  # anonymous
        p1 = self.client.get(URL).data
        self.assertEqual(p1['count'], 6)
        ids = [p['id'] for p in p1['results']]
        self.assertEqual(ids, sorted(ids))
        self.assertEqual(len(p1['results']), 5)
        p2 = self.client.get(URL, {'page': 2}).data
        self.assertEqual(len(p2['results']), 1)
        self.assertEqual(p2['results'][0]['name'], 'Item 6')
