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

'''
Measurement units from DLMS Blue Book
(2017-01-19 EXCERPT DLMS UA 1000-1 Ed. 12.2)
'''

UNITS = {
    1: "Y",
    2: "M",
    3: "W",
    4: "D",
    5: "H",
    6: "M",
    7: "S",
    8: "°",
    9: "°C",
    10: "¤",
    11: "m",
    12: "m/s",
    13: "m³",
    14: "m³ (corr)",
    15: "m³/h",
    16: "m³/h (corr)",
    17: "m³/d",
    18: "m³/d (corr)",
    19: "l",
    20: "kg",
    21: "N",
    22: "Nm",
    23: "Pa",
    24: "bar",
    25: "J",
    26: "J/h",
    27: "W",
    28: "VA",
    29: "var",
    30: "Wh",
    31: "VAh",
    32: "varh",
    33: "A",
    34: "C",
    35: "V",
    36: "V/m",
    37: "F",
    38: "Ω",
    39: "Ωm²/m",
    40: "Wb",
    41: "T",
    42: "A/m",
    43: "H",
    44: "Hz",
    45: "1/(Wh)",
    46: "1/(varh)",
    47: "1/(VAh)",
    48: "V²h",
    49: "A²h",
    50: "kg/s",
    51: "mho",
    52: "K",
    53: "1/(V²h)",
    54: "1/(A²h)",
    55: "1/m³",
    56: "%",
    57: "Ah",
    60: "Wh/m³",
    61: "J/m³",
    62: "Mol%",
    63: "g/m³",
    64: "Pa s",
    65: "J/kg",
    70: "dBm",
    71: "dBµV",
    72: "dB",
    255: "count",
}
