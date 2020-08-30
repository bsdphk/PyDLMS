#!/usr/bin/env python
#
# Copyright (c) 2020 Poul-Henning Kamp <phk@phk.freebsd.dk>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.


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

