from django.test import TestCase
from .models import SessionCoins


class SessionTestCase(TestCase):

    def setUp(self):
        SessionCoins.objects.create(user_id=1, coins=2)


    def test_change_value(self):
        person = SessionCoins.objects.get(user_id=1)
        self.assertEqual(person.coins_operation(1, 2), True)
