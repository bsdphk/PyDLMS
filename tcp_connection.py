
import socket
import time

def hexdump(s):
    ''' Debugging, does what it says on the tin '''
    return "".join("%02x" % a for a in s)

class TcpConnection():

    ''' Connection via plain TCP '''

    def __init__(self, todo, app, host, port):
        self.todo = todo 
        self.app = app
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))
        self.s.settimeout(self.todo.next_timeout())
        app.now_open(self)

        while True:
            self.receive()

    def tx(self, d):
        # print("CTX:", hexdump(d))
        if False and random.randint(0, 99) < 2:
            print("DROP TX" + "=" * 60)
            d[-2] = 0x00
        self.s.sendall(d)

    def receive(self):
        self.s.settimeout(self.todo.next_timeout())
        try:
            a = self.s.recv(100)
            # print("CRX:", hexdump(a))
            self.app.rx_feed(a)
        except socket.timeout:
            pass

