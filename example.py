
import time

import random

import todolist
import tcp_connection
import hdlc_connection
import dlms_connection

from blue_book_units import UNITS
from blue_book_electricity import electricity_names

import parameters

class Cosem():
    def __init__(
        self,
        todo,
        dlms,
        cls,
        obj,
        freq=10,
    ):
        self.todo = todo
        self.dlms = dlms
        self.cls = cls
        self.obj = obj
        self.freq = freq
        self.units = None
        self.next = None
        self.scale = 1.0
        self.dlms.get_cosem(self, 3, self.cb_units)
        self.name = electricity_names(self.obj)
        self.unit = None
        self.fmt = None

    def poll(self):
        self.dlms.get_cosem(self, 2, self.cb_val)

    def cb_units(self, val):
        print("COSEM_UNITS", self, val)
        self.units = val
        self.unit = UNITS[val[1]]
        self.next = time.time() + self.freq
        self.todo.schedule(self.next, self.poll)
        self.scale = 10 ** val[0]
        self.fmt = "%" + ".%df" % (-min(0, val[0]))

    def cb_val(self, val):
        r = self.fmt % (val * self.scale)
        print("COSEM_DATA", "%30s" % str(self), "%12.2f" % val, "%12s %-4s" % (r, self.unit), "%7.3f" % time.time(), self.name)
        self.next += self.freq
        self.todo.schedule(self.next, self.poll)

    def __repr__(self):
        return "<COSEM " + ".".join("%d" % x for x in self.obj) + ">"

def main(points):

    def cb(*args, **kwargs):
        print("CB", *args, **kwargs)

    todo = todolist.ToDo()

    dlms = dlms_connection.DlmsSession(todo)

    for i,j in POINTS.items():
        freq = j[0]
        assert freq
        if freq == 1:
            freq = 3
        cp = Cosem(todo, dlms, 3, i, freq=freq)
        dlms.add_app(cp)

    hdlc = hdlc_connection.HdlcConnection(
        todo=todo,
        app=dlms,
        src_adr=parameters.LLC_SRC,
        dst_adr=parameters.LLC_DST,
    )

    conn = tcp_connection.TcpConnection(
        todo=todo,
        app=hdlc,
        host=parameters.HOST,
        port=parameters.PORT,
    )

RATE_FAST = 3
RATE_SLOW = 10

POINTS = {
    (1, 0,  1,  7,  0, 255, ): ( RATE_FAST, ),
    (1, 0,  1,  8,  0, 255, ): ( RATE_SLOW, ),
    (1, 0,  2,  7,  0, 255, ): ( RATE_FAST, ),
    (1, 0,  2,  8,  0, 255, ): ( RATE_SLOW, ),
    (1, 0, 14,  7,  0, 255, ): ( RATE_SLOW, ),
    (1, 0, 15,  7,  0, 255, ): ( RATE_FAST, ),
    (1, 0, 15,  8,  0, 255, ): ( RATE_SLOW, ),
    (1, 0, 16,  8,  0, 255, ): ( RATE_SLOW, ),

    (1, 0, 21,  7,  0, 255, ): ( RATE_FAST, ),
    (1, 0, 21,  8,  0, 255, ): ( RATE_SLOW, ),
    (1, 0, 22,  7,  0, 255, ): ( RATE_FAST, ),
    (1, 0, 22,  8,  0, 255, ): ( RATE_SLOW, ),
    (1, 0, 23,  7,  0, 255, ): ( RATE_SLOW, ),
    (1, 0, 24,  7,  0, 255, ): ( RATE_SLOW, ),
    (1, 0, 31,  7,  0, 255, ): ( RATE_FAST, ),
    (1, 0, 32,  7,  0, 255, ): ( RATE_FAST, ),

    (1, 0, 41,  7,  0, 255, ): ( RATE_FAST, ),
    (1, 0, 41,  8,  0, 255, ): ( RATE_SLOW, ),
    (1, 0, 42,  7,  0, 255, ): ( RATE_FAST, ),
    (1, 0, 42,  8,  0, 255, ): ( RATE_SLOW, ),
    (1, 0, 43,  7,  0, 255, ): ( RATE_SLOW, ),
    (1, 0, 44,  7,  0, 255, ): ( RATE_SLOW, ),
    (1, 0, 51,  7,  0, 255, ): ( RATE_FAST, ),
    (1, 0, 52,  7,  0, 255, ): ( RATE_FAST, ),

    (1, 0, 61,  7,  0, 255, ): ( RATE_FAST, ),
    (1, 0, 61,  8,  0, 255, ): ( RATE_SLOW, ),
    (1, 0, 62,  7,  0, 255, ): ( RATE_FAST, ),
    (1, 0, 62,  8,  0, 255, ): ( RATE_SLOW, ),
    (1, 0, 63,  7,  0, 255, ): ( RATE_SLOW, ),
    (1, 0, 64,  7,  0, 255, ): ( RATE_SLOW, ),
    (1, 0, 71,  7,  0, 255, ): ( RATE_FAST, ),
    (1, 0, 72,  7,  0, 255, ): ( RATE_FAST, ),

    (1, 0, 81,  7, 10, 255, ): ( RATE_SLOW, ),
    (1, 0, 81,  7, 20, 255, ): ( RATE_SLOW, ),
    (1, 0, 81,  7, 21, 255, ): ( RATE_SLOW, ),
    (1, 0, 81,  7, 40, 255, ): ( RATE_SLOW, ),
    (1, 0, 81,  7, 51, 255, ): ( RATE_SLOW, ),
    (1, 0, 81,  7, 62, 255, ): ( RATE_SLOW, ),

    (1, 0, 91,  7,  0, 255, ): (  1, ),
}

if __name__ == "__main__":
    main(POINTS)
