from rest_framework.test import APITestCase

from django.contrib.auth.models import User
from django.core import serializers

from promoapp.models import Promo
from promoapp.serializers import UserSerializer

class PromoCreateTestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('john', 'john@snow.com', 'johnpassword')
        self.client.login(username='john', password='johnpassword')
        self.normal_user = User.objects.create_user('m@m.com', 'john', '1234')

    def test_create_promo_admin(self):
        initial_promo_count = Promo.objects.count()
        promo_details = {
            'name': 'Promo A',
            'points': 20,
            'recipient': self.normal_user.pk,
        }
        response = self.client.post('/api/v1/promos/add/', promo_details, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Promo.objects.count(), initial_promo_count + 1)
        for key, value in promo_details.items():
            self.assertEqual(response.data[key], value)
    
    def test_create_promo_normal_user(self):
        self.client.login(username='m@m.com', password='1234')
        initial_promo_count = Promo.objects.count()
        promo_details = {
            'name': 'Promo A',
            'points': 20,
            'recipient': self.normal_user.pk,
        }
        response = self.client.post('/api/v1/promos/add/', promo_details, format='json')
        self.assertEqual(response.status_code, 403)


class PromoListTestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('john', 'john@snow.com', 'johnpassword')
        self.client.login(username='john', password='johnpassword')
        self.normal_user_1 = User.objects.create_user('m@m.com', 'john', '1234')
        self.normal_user_2 = User.objects.create_user('m@yahoo.com', 'john', '5678')
        self.Promo_1 = Promo.objects.create(name='Promo 1', points=20, recipient=self.normal_user_1)
        self.Promo_2 = Promo.objects.create(name='Promo 2', points=50, recipient=self.normal_user_2)

    def test_list_all_promo_admin(self):
        response = self.client.get('/api/v1/promos/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Promo.objects.count(), len(response.data))
    
    def test_list_all_promos_normal_user(self):
        self.client.login(username='m@m.com', password='1234')
        response = self.client.get('/api/v1/promos/')
        self.assertEqual(Promo.objects.filter(recipient__id=self.normal_user_1.pk).count(), len(response.json()))


class PromoDeleteTestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('john', 'john@snow.com', 'johnpassword')
        self.client.login(username='john', password='johnpassword')
        self.normal_user = User.objects.create_user('m@m.com', 'john', '1234')
        self.Promo_1 = Promo.objects.create(name='Promo 1', points=20, recipient=self.normal_user)

    def test_delete_promo_admin(self):
        initial_promos_count = Promo.objects.count()
        promo_id = Promo.objects.first().id
        response = self.client.delete('/api/v1/promos/{}/'.format(promo_id))
        self.assertEqual(Promo.objects.count(), initial_promos_count - 1)
        self.assertRaises(Promo.DoesNotExist, Promo.objects.get, id=promo_id)        

    def test_delete_promo_normal_user(self):
        self.client.login(username='m@m.com', password='1234')
        promo_id = Promo.objects.filter(recipient__id=self.normal_user.pk)[0].id
        response = self.client.delete('/api/v1/promos/{}/'.format(promo_id))
        self.assertEqual(response.status_code, 403)

class PromoUpdateTestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('john', 'john@snow.com', 'johnpassword')
        self.client.login(username='john', password='johnpassword')
        self.normal_user = User.objects.create_user('m@m.com', 'john', '1234')
        self.Promo_1 = Promo.objects.create(name='Promo 1', points=20, recipient=self.normal_user)

    def test_update_promo_admin(self):
        promo_id = Promo.objects.first().id
        response = self.client.patch('/api/v1/promos/{}/'.format(promo_id), {'name': 'Promo 2'}, format='json')
        promo = Promo.objects.get(id=promo_id)
        self.assertEqual(promo.name, 'Promo 2')
    
    def test_update_promo_normal_user(self):
        self.client.login(username='m@m.com', password='1234')
        promo_id = Promo.objects.filter(recipient__id=self.normal_user.pk)[0].id
        response = self.client.patch('/api/v1/promos/{}/'.format(promo_id), {'name': 'Promo 2'}, format='json')
        self.assertEqual(response.status_code, 403)


class GetPromoRemainingPointsTestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('john', 'john@snow.com', 'johnpassword')
        self.client.login(username='john', password='johnpassword')
        self.normal_user_1 = User.objects.create_user('m@m.com', 'john', '1234')
        self.normal_user_2 = User.objects.create_user('m@yahoo.com', 'john', '5678')
        self.Promo_1 = Promo.objects.create(name='Promo 1', points=20, recipient=self.normal_user_1)
        self.Promo_2 = Promo.objects.create(name='Promo 2', points=50, recipient=self.normal_user_2)

    def test_get_promo_remaining_points_admin(self):
        promo_id = Promo.objects.first().id
        response = self.client.get('/api/v1/promos/{}/points/'.format(promo_id))
        self.assertEqual(response.json()['Remaining points'], self.Promo_1.points - self.Promo_1.points_used)
    
    def test_get_promo_remaining_points_normal_user_recipient(self):
        self.client.login(username='m@m.com', password='1234')
        promo_id = Promo.objects.filter(recipient__id=self.normal_user_1.pk)[0].id
        response = self.client.get('/api/v1/promos/{}/points/'.format(promo_id))
        self.assertEqual(response.json()['Remaining points'], self.Promo_1.points - self.Promo_1.points_used)
    
    def test_get_promo_remaining_points_normal_user_not_recipient(self):
        self.client.login(username='m@m.com', password='1234')
        promo_id = Promo.objects.filter(recipient__id=self.normal_user_2.pk)[0].id
        response = self.client.get('/api/v1/promos/{}/points/'.format(promo_id))
        self.assertEqual(response.status_code, 403)


class UsePromoPointsTestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('john', 'john@snow.com', 'johnpassword')
        self.client.login(username='john', password='johnpassword')
        self.normal_user_1 = User.objects.create_user('m@m.com', 'john', '1234')
        self.normal_user_2 = User.objects.create_user('m@yahoo.com', 'john', '5678')
        self.Promo_1 = Promo.objects.create(name='Promo 1', points=20, recipient=self.normal_user_1)
        self.Promo_2 = Promo.objects.create(name='Promo 2', points=50, recipient=self.normal_user_2)

    def test_use_promo_points_admin_enough_points(self):
        response = self.client.get('/api/v1/promos/{}/use/8/'.format(self.Promo_1.id))
        self.promo_1_updated = Promo.objects.get(id=self.Promo_1.id)
        self.assertEqual(response.json()['Remaining points'], self.promo_1_updated.points - self.promo_1_updated.points_used)
    
    def test_use_promo_points_admin_not_enough_points(self):
        response = self.client.get('/api/v1/promos/{}/use/30/'.format(self.Promo_1.id))
        self.assertEqual(response.status_code, 400)
    
    def test_use_promo_points_normal_user_enough_points_recipient(self):
        self.client.login(username='m@m.com', password='1234')
        promo_id = Promo.objects.filter(recipient__id=self.normal_user_1.pk)[0].id
        response = self.client.get('/api/v1/promos/{}/use/8/'.format(promo_id))
        self.promo_updated = Promo.objects.filter(recipient__id=self.normal_user_1.pk)[0]
        self.assertEqual(response.json()['Remaining points'], self.promo_updated.points - self.promo_updated.points_used)
    
    def test_use_promo_points_normal_user_not_enough_points_recipient(self):
        self.client.login(username='m@m.com', password='1234')
        promo_id = Promo.objects.filter(recipient__id=self.normal_user_1.pk)[0].id
        response = self.client.get('/api/v1/promos/{}/use/30/'.format(promo_id))
        self.assertEqual(response.status_code, 400)
    
    def test_use_promo_points_normal_user_enough_points_not_recipient(self):
        self.client.login(username='m@m.com', password='1234')
        promo_id = Promo.objects.filter(recipient__id=self.normal_user_2.pk)[0].id
        response = self.client.get('/api/v1/promos/{}/use/8/'.format(promo_id))
        self.assertEqual(response.status_code, 403)
    
    def test_use_promo_points_normal_user_not_enough_points_not_recipient(self):
        self.client.login(username='m@m.com', password='1234')
        promo_id = Promo.objects.filter(recipient__id=self.normal_user_2.pk)[0].id
        response = self.client.get('/api/v1/promos/{}/use/30/'.format(promo_id))
        self.assertEqual(response.status_code, 403)


