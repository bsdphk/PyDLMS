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
We only need to transmit two different kinds of frames, and I have
implemented ASN.1/BER more times than anybody needs already, so
here we just lay the AARQ frame out manually.

Do not email about this file, unless you include a patch to improve it.
'''

from parameters import PASSWORD

def iterable(obj):
    ''' Is this object iterable '''
    try:
        iter(obj)
    except Exception:
        return False
    else:
        return True

def compose(a):
    '''
       Recursively compose a list, such that sub-lists gets
       prefixed by their length
    '''
    r = []
    for i in a:
        if iterable(i):
            j = compose(i)
            r.append(len(j))
            r += j
        else:
            r.append(i)
    return r

# Look in the back of (IS/)IEC 62056-53 : 2006 for what this might,
# or might not, mean.  Hack until your power-meter does not puke.

AARQ = compose(
    [
        0xe6, 0xe6, 0x00,			# Green Book LLC header (fig 19)
        0x60, [					# AARQ
            0xa1, [				# Application Context name
                0x06, [				# OID
                    0x60, 0x85, 0x74, 0x05, 0x08, 0x01, 0x01,
                ]
            ],
            0x8a, [				# ACS-requirements
                0x07, 0x80,
            ],
            0x8b, [				# Mechanism-name
                0x60, 0x85, 0x74, 0x05, 0x08, 0x02, 0x01,
            ],
            0xac, [				# Authentication-Value
                0x80, PASSWORD.encode("ASCII"),
            ],
            0xbe, [				# User Information
                0x04, [				# OCTET STRING
                    0x01,			# Initiate Request
                    0x00,			# OCTET STRING OPTIONAL `decicated-key`
                    0x00,			# BOLEAN `response allowed`
                    0x00,			# Integer8 `proposed-quality-of-service`
                    0x06,			# Unsigned 8 `proposed-dlms-version-number`
                    0x5F, 0x1F,	[		# [APPLICATION 31]
                        0x00,			# unused bits in last octet
                        0x00, 0x10, 0x10,	# bitmap
                    ],
                    0xFF, 0xFF			#  Unsigned16 `client-max-receive-pdu-size`
                ],
            ],
        ],
    ]
)
