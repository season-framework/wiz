import os
fs = wiz.project.fs(os.path.join("config", "pwa"))
swjs = fs.read("sw.js", "")
wiz.response.send(swjs, content_type="text/javascript; charset=utf-8")
