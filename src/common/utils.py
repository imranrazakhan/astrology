
def decimal_to_dms(dec, type="3"):
    dec = float(dec)
    a = int(dec)
    a_new = (dec-float(a)) * 60.0
    b_rounded = int(round(a_new))
    b = int(a_new)
    c = int(round((a_new-float(b))*60.0))
    if type == "3":
        out = '{}º{}\'{}"'.format(a, b, c)
    elif type == "2":
        out = '{}º{}\''.format(a, b_rounded)
    elif type == "1":
        out = '{}º'.format(a)
    return str(out)