from unittest import TestCase
from unittest.mock import patch

from .user import Controller

class TestController(TestCase):
	def setUp(self):
		self.ctrl = Controller()

	def test_unknown(self):
		chat_id = 12345678
		ret_chat_id, ret_str = self.ctrl.processCommand(chat_id, "blabla")

		self.assertEqual(chat_id, ret_chat_id)
		self.assertEqual(ret_str, "I do not understand you, mate!")

	@patch('django.template.loader')
	def test_hello(self, mock_loader):
		chat_id = 87654321
		ret_chat_id, ret_str = self.ctrl.processCommand(chat_id, "/info")

	    # test that processCommand called render_to_string with the right parameters
		mock_loader.render_to_string.assert_called_with('talktome/hello.md')
		self.assertEqual(chat_id, ret_chat_id)
