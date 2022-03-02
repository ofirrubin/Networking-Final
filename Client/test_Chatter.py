from unittest import TestCase

from Client.Chatter import Chatter
from Server.__main__ import Chat

IP = "127.0.0.1"
PORT = 15003
SERVER_DIR = r"..\Server\Data"
server = Chat(IP, PORT, "", False)
server.start()
cl1n = "===========TEST1============="
cl2n = "===========TEST2============="
client1 = Chatter(IP, PORT, print, print, print, print, print)
client1.login(cl1n)


class TestChatter(TestCase):

    def setUp(self) -> None:
        # Set to print as callbacks
        self.client2 = Chatter(IP, PORT, self.on_update, self.on_users_changed, self.msg_sent, print, print)

    def test_login(self):
        self.client2.login(cl2n)
        self.assertTrue(self.client2.logged_in)

    def test__set_list_files(self):
        files = list(server.db.list_files())
        self.assertEqual(files, self.client2.list_files)

    def test_message(self):
        client1.message(cl2n, "Hi")
        self.client2.message(cl1n, "Hi")

    def msg_sent(self, verified, feedback, msg):
        self.assertTrue(verified)

    def on_update(self, updates, failed):
        for u in updates:
            sender, msg = u.split("\n", maxsplit=1)
            if sender != '':  # Direct Message, otherwise Broadcast
                self.assertEqual(sender, cl2n)
            self.assertEqual(msg.replaace("+", "", 1).replace("-", "", 1), "Hi")

    def on_users_changed(self, logged_in, logged_out):
        if logged_in:
            self.assertTrue(cl1n in logged_in)
        if logged_out:
            self.assertTrue(cl1n in logged_out)

    def test_broadcast(self):
        client1.broadcast("Hi")
        self.client2.broadcast("Hi")

    def tearDown(self) -> None:
        self.client2.logout()


client1.logout()
server.stop()
