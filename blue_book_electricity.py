
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
