from django.test import TestCase, RequestFactory
from .models import Account, CustomUser
from .views import *


class UserTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = CustomUser.objects.create(username='Laz', email='Y@gmail.com',
                                                password='Elik1993')

    def test_1(self):
        request = self.factory.get('/')
        request.user = self.user
        response = HomeView.as_view()(request)
        self.assertEqual(response.status_code, 200)


