import socket
import threading
from time import sleep

import rsa

import AES
import ClientHandler
from Chat import DatabaseConnection as Database


class SecurePipe:
    ENC = 512

    def __init__(self, conn, server_side=True):
        self.conn = conn
        self.aes = None
        self.secured = False
        if server_side is True:
            self.secured = self.server_handshake()
        else:
            self.secured = self.client_handshake()

    @classmethod
    def connect(cls, ip, port):
        conn = socket.socket()
        conn.connect((ip, port))
        return SecurePipe(conn, server_side=False)

    def client_handshake(self):
        pub_key = self.conn.recv(self.ENC)
        pub_key = rsa.PublicKey.load_pkcs1(pub_key)
        k = AES.AESCipher.random_base()
        aes = AES.AESCipher(k)
        self.conn.sendall(rsa.encrypt(k, pub_key))
        d = self.conn.recv(256)
        if "KEY_SWAP".encode() != aes.decrypt(d):
            self.conn.sendall(rsa.encrypt("FALSE".encode(), pub_key))
            return False
        self.aes = aes
        self.conn.sendall(aes.encrypt("PAWS_YEK".encode()))
        return True

    def server_handshake(self):
        pub_key, pri_key = rsa.newkeys(self.ENC)
        # Server generates RSA key for single use, client is encrypting AES key
        # and sending it to the server, server uses the AES key to send a verification
        # to the client, if the client verifies (able to decrypt) then it sends encrypted OK msg to the server.
        # if the server able to decrypt too, it is verified and handshake successed.
        self.conn.sendall(pub_key.save_pkcs1())  # Message size = Key Size
        try:
            key = self.conn.recv(self.ENC)
            key = rsa.decrypt(key, pri_key)
        except (socket.error, rsa.DecryptionError):
            try:
                self.conn.close()
            except socket.error:
                pass
            return False

        aes = AES.AESCipher(key)
        self.conn.sendall(aes.encrypt("KEY_SWAP".encode()))
        try:
            if "PAWS_YEK".encode() == aes.decrypt(self.conn.recv(256)):
                self.aes = aes
                return True
        except Exception:
            pass
        return False

    def send(self, data):
        e = self.aes.encrypt(data)
        length = int.to_bytes(len(e), 8, "big")
        self.conn.sendall(self.aes.encrypt(length))
        self.conn.sendall(e)
        sleep(0.5)

    def recv(self):
        try:
            b = self.conn.recv(44)
            a = self.aes.decrypt(b)
            size = int.from_bytes(a, byteorder="big")
            a = self.conn.recv(size)
            return self.aes.decrypt(a)
        except ValueError:
            return b''

    def close(self):
        self.conn.close()


class Server:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.sock = socket.socket()
        self.__running = False

    def start(self, user_handler):
        self.sock.bind((self.ip, self.port))
        self.sock.listen(100)  # How many clients to listen, queue size.
        self.__running = True
        while self.__running is True:
            client, addr = self.sock.accept()
            threading.Thread(target=user_handler, args=(client, addr), daemon=False).start()

    def stop(self):
        self.__running = False


class ChatServer:
    def __init__(self, ip, port, **args):
        self.ip = ip
        self.port = port
        self.server = Server(self.ip, self.port)
        self.db = Database(**args)

    def client_handler(self, conn, addr):
        # User handler
        print("<{ip}, {port}> Server: Connection from <{client}>".format(ip=self.ip, port=self.port, client=addr))
        print("Securing connection")
        connection = SecurePipe(conn, server_side=True)
        print("Connection secured" if connection.secured else "Connection is not secured")
        ClientHandler.ClientHandler(self, connection).handle()
        conn.close()

    def start(self):
        self.server.start(user_handler=self.client_handler)

    def stop(self):
        self.server.stop()

