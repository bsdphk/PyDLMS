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

import struct
import time

# To set a password, see this file:
from asn1sucks import AARQ
from blue_book_units import UNITS

def hexdump(s):
    ''' Debugging, does what it says on the tin '''
    return "".join("%02x" % a for a in s)


class DlmsSession():

    ''' A DLMS Green Book Session '''

    def __init__(
        self,
        todo,
    ):
        self.hdlc = None
        self.todo = todo

        self.state = {}

        self.apps = []

        self.todolist = []
        self.busy = True

    def add_app(self, app):
        self.apps.append(app)

    def next(self):
        if self.busy or not self.todolist:
            return
        self.busy = True
        j = self.todolist[0]
        self.state = {
            "DATA": j[2],
        }
        j[0](*j[1])

    def get_cosem(self, cp, attr, callback):
        self.todolist.append([self.tx_cosem_get_request, (cp.cls, cp.obj, attr), callback])
        self.next()

    def now_open(self, hdlc):
        self.hdlc = hdlc
        self.busy = True
        self.tx_aarq()

    def open_apps(self):
        self.busy = False
        self.next()

    def tx_aarq(self):
        ''' DLMS Green Book::A-Associate Request '''
        self.hdlc.tx_i(AARQ)
        self.state = {
            "HACK": self.open_apps,
        }

    def rx_i_pdu(self, pdu):
        # DLMS Green Book 8.3.2

        if pdu[0] != 0xe6:
            print("DLMS wrong LLC_DST", hexdump(pdu))
            return
        if pdu[1] not in (0xe6, 0xe7):
            print("DLMS wrong LLC_SRC", hexdump(pdu))
            return
        if pdu[2]:
            print("DLMS LLC_CTRL", hexdump(pdu))
            return

        # DLMS_UA_SCHEMA_2018_08_21
        if not self.dlsm_pdu(pdu[3:]):
            # print("DLMS ???\t", hexdump(pdu))
            # Yeah, we ought to decode this but who cares...
            t = self.state.get("HACK")
            if t:
                t()

    def dlsm_pdu(self, pdu):
        if pdu[0] == 0xc4 and pdu[1] == 1 and pdu[3] == 0:
            # DLMS_UA_SCHEMA_2018_08_21
            val = self.asn1_data(pdu[4:])
            t = self.state.get("DATA")
            if t:
                t(val)
            self.busy = False
            self.todolist.pop(0)
            self.next()
            return True
        if pdu[0] == 0xc4 and pdu[1] == 1 and pdu[3] == 1:
            # DLMS_UA_SCHEMA_2018_08_21
            e = self.asn1_data_access_result(pdu[4:])
            print("ACCESS ERROR", e)
            return True

    def asn1_data_access_result(self, pdu):
        e = {
            0: "success",
            1: "hardware-fault",
            2: "temporary-failure",
            3: "read-write-denied",
            4: "object-undefined",
            9: "object-class-inconsistent",
            11: "object-unavailable",
            12: "type-unmatched",
            13: "scope-of-access-violated",
            14: "data-block-unavailable",
            15: "long-get-aborted",
            16: "no-long-get-in-progress",
            17: "long-set-aborted",
            18: "no-long-set-in-progress",
            19: "data-block-number-invalid",
            250: "other-reason",
        }.get(pdu[0])
        if not e:
            e = "reason=0x%x" % pdu[0]
        return e

    def asn1_data(self, pdu):
        '''
        Extract data from a data point
        See: DLMS_UA_SCHEMA_2018_08_21
        '''
        val, pdu = self.asn1_data_atom(pdu)
        if val is not None and not pdu:
            return val
        if pdu[0] == 2:
            # structure (SEQUENCE)
            n = pdu[1]
            pdu = pdu[2:]
            l = []
            for _i in range(n):
                x, y = self.asn1_data_atom(pdu)
                l.append(x)
                pdu = y
            return l
        print("\t??DATA", val, " ".join(["%02x" % x for x in pdu]))

    def asn1_data_atom(self, pdu):
        '''
        Extract an atomic value from a data point
        See: DLMS_UA_SCHEMA_2018_08_21
        '''
        st = {
            0x05: ">l",
            0x06: ">L",
            0x0f: ">b",
            0x12: ">H",
            0x16: ">B",
        }.get(pdu[0])
        if st:
            l = struct.calcsize(st)
            return (struct.unpack(st, pdu[1:1+l])[0], pdu[1+l:])
        if pdu[0] == 9:
            # OCTET STRING
            l = pdu[1]
            return (pdu[2:2+l], pdu[2+l:])
        return None, pdu

    def tx_cosem_get_request(self, cosem_class, cosem_object, cosem_attribute):
        ''' DLMS Green Book::COSEM GET request '''
        assert len(cosem_object) == 6
        self.hdlc.tx_i(
           [
           0xE6, 0xE6, 0x00,	# Green Book LLC header (fig 19)
           0xC0, 0x01,		# Get-Request-Normal
           0xC1,		# `invoke-id-and-priority`
           cosem_class >> 8,
           cosem_class & 0xff,
           ] + list(cosem_object) + [
           cosem_attribute,
           0x00
           ]
       )
