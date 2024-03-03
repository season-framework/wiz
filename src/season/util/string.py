import string as _string
import random as _random
import datetime

def random(length=12):
    string_pool = _string.ascii_letters + _string.digits
    result = ""
    for i in range(length):
        result += _random.choice(string_pool)
    return result

def addtabs(v, size=1):
    for i in range(size):
        v =  "    " + "\n    ".join(v.split("\n"))
    return v

def json_default(value): 
    if isinstance(value, datetime.date): 
        return value.strftime('%Y-%m-%d %H:%M:%S') 
    return str(value)

def translate_id(value):
    value = value.replace("/", ".").replace(" ", "")
    allowed = "qwertyuiopasdfghjklzxcvbnm.1234567890"
    nvalue = ""
    for c in value:
        if c not in allowed:
            nvalue = nvalue
        else:
            nvalue = nvalue + c
    if nvalue[0] == ".": nvalue = nvalue[1:]
    if len(nvalue) == 0: nvalue = "index"
    return nvalue
