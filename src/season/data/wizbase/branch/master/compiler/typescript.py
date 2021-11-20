import dukpy

def compile(wiz, js, data):
    js = dukpy.typescript_compile(js)
    js = str(js)
    js = '\n'.join(js.split('\n')[5:-4])
    return js