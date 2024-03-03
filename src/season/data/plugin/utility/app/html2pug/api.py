import os

def html2pug():
    html = wiz.request.query("html", True)
    html = html.replace('"', "\\\"")
    buildpath = wiz.ide.fs("build").abspath()
    cmd = f"let html2pug = require('html2pug'); console.log(html2pug(\\`{html}\\`, " + '{ tabs: 4, fragment: true }' + "));"
    cmd = f'cd {buildpath} && node -e "{cmd}"'
    text = os.popen(cmd).read()
    wiz.response.status(200, text)
