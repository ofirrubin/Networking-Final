from time import sleep

from Server import SecurePipe


class Client:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.connection = None

    def login(self, username, password):
        if "\n" in username or "\n" in password:
            raise ValueError("Username nor password can include new line.")
        self.connection = SecurePipe.connect(self.ip, self.port)
        self.connection.send(username.encode() + "\n" + password.encode())


c = Client("127.0.0.1", 5551)
c.login(100*"username", "password")
