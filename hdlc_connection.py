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

import crcmod

import random

# The HDLC CRC function
CCITT_CRC16 = crcmod.mkCrcFun(0x11021, initCrc=0, xorOut=0xffff)

FLAG = 0x7e                     # ISO13239

def hexdump(s):
    ''' Debugging, does what it says on the tin '''
    return "".join("%02x" % a for a in s)

def mk_hdlc(adr1, adr2, ctrl, body=None):
    '''
    Build an ISO13239 Type 3 frame:
        {FLAG hdr HCS [body LCS] FLAG}
    '''
    frame_len = 5 + 2
    if body:
        frame_len += len(body) + 2
    assert frame_len <= 0x7ff
    b = bytearray()
    b.append(FLAG)
    b.append(0xa0 | (frame_len >> 8))
    b.append(frame_len & 0xff)
    b.append(adr1 << 1 | 1)
    b.append(adr2 << 1 | 1)
    b.append(ctrl)
    crc = CCITT_CRC16(b[1:])
    b.append(crc & 0xff)
    b.append(crc >> 8)
    if body:
        b += bytearray(body)
        crc = CCITT_CRC16(b[1:])
        b.append(crc & 0xff)
        b.append(crc >> 8)
    b.append(FLAG)
    return b

class HdlcConnection():

    ''' A ISO13239 ISO Connection '''

    def __init__(
            self,
            todo,
            app,
            src_adr=0x01,
            dst_adr=0x20,
        ):
        self.todo = todo
        self.phys = None
        self.app = app

        self.lla_src = src_adr
        self.lla_dst = dst_adr

        self.rx_frame = bytearray()
        self.rx_ns = 0
        self.rx_nr = 0

        self.tx_ns = 0
        self.tx_nr = 0
        self.tx_last = None

        self.state = { }

        self.tmojob = None

    def now_open(self, phys):
        self.phys = phys
        self.tx_disc()

    ###################################################################
    # Receive
    ###################################################################

    def rx_feed(self, a):
        ''' Reassemble ISO13239 HDLC frames '''

        # print("*", hexdump(a))

        if False and random.randint(0, 99) < 3:
            print("DROP RX" + "-" * 60)
            return
        self.rx_frame += bytearray(a)

        prune, diag = self.validate_hdlc_frame(self.rx_frame)

        if diag:
            print("HDLC " + diag)

        if prune:
            self.rx_frame = self.rx_frame[prune:]

        return prune and not diag

    def validate_hdlc_frame(self, pdu):
        ''' Validate and process good ISO13239 Type 3 HDLC frames '''

        # Skip until first byte is a FLAG
        i = pdu.find(FLAG)
        if i < 0:
            return len(pdu), "No FLAG"
        if i > 0:
            return i, "FLAG not at start"

        # Wait until we have FLAG + CTRL + 2LEN + 2ADR + 2FCS
        if len(pdu) < 8:
            return 0, None

        # Validate the HCS before we touch the fields
        crc = CCITT_CRC16(pdu[1:6])
        if (crc & 0xff) != pdu[6] or (crc >> 8) != pdu[7]:
            return 1, "HCS mismatch"

        # ISO13239 Type 3 ?
        if pdu[1] & 0xf0 != 0xa0:
            return 1, "Not Type 3 frame"

        # Check address fields
        if pdu[3] != (self.lla_dst << 1) | 1:
            return 1, "LLA_DST 0x%02x" % pdu[3]
        if pdu[4] != (self.lla_src << 1) | 1:
            return 1, "LLA_SRC 0x%02x" % pdu[4]

        # Wait until we have the full frame
        flength = (pdu[1] & 0x07) << 8
        flength |= pdu[2]
        if len(pdu) < 2 + flength:
            return 0, None

        # And the terminating FLAG
        if pdu[1 + flength] != FLAG:
            return 0, None

        # Validate LCS
        crc = CCITT_CRC16(pdu[1:flength - 1])
        if (crc & 0xff) != pdu[flength - 1] or (crc >> 8) != pdu[flength]:
            return 1, "LCS"

        # Got a valid HDLC frame
        self.process_hdlc_frame(pdu[1:6], pdu[8:flength - 1])
        return 2 + flength, None

    def process_hdlc_frame(self, hdr, body):
        if not hdr[4] & 0x01:
            self.rx_i(hdr, body)
        elif not hdr[4] & 0x02:
            self.rx_s(hdr, body)
        else:
            self.rx_u(hdr, body)

    def rx_s(self, hdr, body):
        ''' ISO13239::Supervisory Frame'''
        print("\nRX S???\t", hexdump(hdr), "|", hexdump(body))

    def rx_u(self, hdr, body):
        ''' ISO13239::Unnumbered Frame'''
        typ = {
            0x63: "UA",         # Unnumbered Acknowledge
            0x87: "FRMR",       # Frame Reject
            0x0f: "DM",         # Disconnected Mode Response
            0x43: "RD",         # Request Disconnect Response
            0x47: "RIM",        # Request Initialization Mode Response
            0x03: "UI",         # Unnumbered Information Response
            0xaf: "XID",        # Exchange Identification Response
            0xe3: "TEST",       # Test Response
            0xef: "UIH",        # Unnumbered Information with header check
        }.get(hdr[4] & 0xef)

        if not typ:
            typ = "?0x%02x" % hdr[4]

        if typ == "FRMR":
            typ += "_%x" % (body[2] & 0xf)
        
        # print("\nRX %s\t" % typ, hexdump(hdr), "|", hexdump(body))
        nxt = self.state.get(typ)
        if nxt:
            nxt()
        else:
            print("NO state[%s]" % typ)
            self.tx_disc()

    def rx_i(self, hdr, body):
        ''' ISO13239::Information Transfer '''
        # print("\nRX I\t", hexdump(hdr), "|", hexdump(body))
        assert hdr[4] & 0x10, "No P/F"
        self.rx_nr = hdr[4] >> 5
        self.rx_ns = (hdr[4] >> 1) & 0x7
        if self.rx_nr == (1 + self.tx_ns) & 7:
            self.tx_ns = (1 + self.tx_ns) & 7
            self.tx_last = None

        self.tmojob = self.todo.cancel(self.tmojob)
        self.app.rx_i_pdu(body)

    ###################################################################
    # Transmit
    ###################################################################

    def tx_ctrl(self):
        ctrl = self.tx_nr << 5
        ctrl |= 0x10
        ctrl |= self.tx_ns << 1
        # print("  C %02x %d|%d" % (ctrl, self.tx_nr, self.tx_ns))
        return ctrl

    def repeat(self):
        print("HDLC REPEAT")
        print("Repeat", hexdump(self.tx_last))
        self.phys.tx(self.tx_last)
        self.tmojob = self.todo.cancel(self.tmojob)
        self.tmojob = self.todo.schedule(10, self.tx_disc)

    def tx_with_repeat(self, pdu):
        self.tx_last = pdu
        self.phys.tx(self.tx_last)
        self.tmojob = self.todo.cancel(self.tmojob)
        self.tmojob = self.todo.schedule(3, self.repeat)

    def timeout2(self):
        print("HDCL TIMEOUT2")
        self.tx_ns = (1 + self.tx_ns) & 7
        self.tx_nr = (1 + self.tx_nr) & 7
        self.state["FRMR_8"] = self.tx_disc
        self.phys.tx(
            mk_hdlc(
                self.lla_src,
                self.lla_dst,
                self.tx_ctrl(),
                self.tx_last,
            )
        )
        self.tmojob = self.todo.cancel(self.tmojob)
        self.tmojob = self.todo.schedule(10, self.tx_disc)

    def timeout(self):
        '''
        At least my L&G E450 meter cannot retransmit at all.

        If you retransmit, it will return FRMR+z which is patently wrong.

        If you try to probe it with an REJ you get two 0x00 bytes back ?!

        If you try to force a resend by sending the next query, it also
        sends FRMR+z

        So we retransmit, in case our packet got lost, if that gets us
	FRMR+z, we send the query again with new sequence numbers.

        If that gets us FRMR+z we just give up and DISC

        Why the even bother using HDLC procedures in the first place ?!
	'''
        print("HDLC TIMEOUT")
        self.state["FRMR_8"] = self.timeout2
        self.phys.tx(
            mk_hdlc(
                self.lla_src,
                self.lla_dst,
                self.tx_ctrl(),
                self.tx_last,
            )
        )
        self.tmojob = self.todo.cancel(self.tmojob)
        self.tmojob = self.todo.schedule(10, self.tx_disc)

    def tx_with_retry(self, body):
        self.tx_last = body
        self.phys.tx(
            mk_hdlc(
                self.lla_src,
                self.lla_dst,
                self.tx_ctrl(),
                self.tx_last,
            )
        )
        self.tmojob = self.todo.cancel(self.tmojob)
        self.tmojob = self.todo.schedule(3, self.timeout)

    def tx_disc(self):
        ''' ISO13239::Disconnect'''
        # print("TX DISC", hexdump(self.rx_frame))
        self.rx_frame = bytearray()
        self.state = {
            "UA": self.tx_disc,
            "DM": self.tx_snrm,
        }
        self.tx_with_repeat(
            mk_hdlc(
                self.lla_src,
                self.lla_dst,
                0x43,   # SNRM + Poll
            )
        )

    def open_app(self):
        self.tmojob = self.todo.cancel(self.tmojob)
        self.app.now_open(self)

    def tx_snrm(self):
        ''' ISO13239::Set Normal Response Mode '''

        # print("TX SNRM")
        self.rx_ns = 7
        self.rx_nr = 0
        self.tx_ns = 0
        self.tx_nr = 0

        self.state = {
            "UA": self.open_app,
        }

        self.tx_with_repeat(
            mk_hdlc(
                self.lla_src,
                self.lla_dst,
                0x93,   # SNRM + Poll
            )
        )

    def tx_i(self, body):
        ''' ISO13239::Information Transfer '''
        self.tx_nr = (1 + self.rx_ns) & 7
        # print("TX I")
        self.tx_with_retry(body)
