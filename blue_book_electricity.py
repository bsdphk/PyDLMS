opyright (c) 2020 Poul-Henning Kamp <phk@phk.freebsd.dk>
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

''' Magic numbers from DLMS/COSEM "Blue Book" '''

GROUP_C = {
    1: "Active power+ (QⅠ+QⅣ)",
    2: "Active power+ (QⅡ+QⅢ)",
    3: "Reactive power+ (QⅠ+QⅣ)",
    4: "Reactive power+ (QⅡ+QⅢ)",
    11: "Current",
    12: "Voltage",
    14: "Frequency",
    15: "Active power abs(QⅠ+QⅣ)+abs(QⅡ+QⅢ)",
    16: "Active power abs(QⅠ+QⅣ)-abs(QⅡ+QⅢ)",
}

GROUP_D = {
    7: "Instant",
    8: "Billing",
}

GROUP_E_ANGELS = {
    0: "U(L\u2081)",
    1: "U(L\u2082)",
    2: "U(L\u2083)",
    4: "I(L\u2081)",
    5: "I(L\u2082)",
    6: "I(L\u2083)",
    7: "I(L\u2080)",
};

def electricity_names(oid):
    assert len(oid) == 6

    if oid[0] != 1:
        return ".".join("%d" % x for x in oid)

    if oid[1] != 0:
        return ".".join("%d" % x for x in oid)

    a = None
    b = None
    if oid[2] <= 20:
        a = GROUP_C.get(oid[2])
        b = "Total"
    elif oid[2] <= 40:
        a = GROUP_C.get(oid[2] - 20)
        b = "L\u2081"
    elif oid[2] <= 60:
        a = GROUP_C.get(oid[2] - 40)
        b = "L\u2082"
    elif oid[2] <= 80:
        a = GROUP_C.get(oid[2] - 60)
        b = "L\u2083"
    elif oid[2] == 81:
        x = GROUP_E_ANGELS[oid[4] // 10]
        y = GROUP_E_ANGELS[oid[4] % 10]
        if x and y:
            a = "°"
            b = x + "→" + y
    elif oid[2] == 91:
        a = "Current"
        b = "L\u2080"

    c = GROUP_D.get(oid[3])

    if not a or not c:
        return ".".join("%d" % x for x in oid)

    return ", ".join((a, b, c))
