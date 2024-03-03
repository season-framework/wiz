import urllib

class Uri:
    def __init__(self, wiz):
        self._wiz = wiz

        baseurl = wiz.server.config.boot.route.base
        if len(baseurl) > 0 and baseurl[-1] == "/": baseurl = baseurl[:-1]
        ideurl = wiz.server.config.boot.route.ide
        if len(ideurl) > 0 and ideurl[-1] == "/": ideurl = ideurl[:-1]
        asseturl = wiz.server.config.boot.route.asset
        if len(asseturl) > 0 and asseturl[-1] == "/": asseturl = asseturl[:-1]

        self._base = baseurl
        self._ide = ideurl
        self._asset = asseturl

    def _path(self, *args):
        paths = []
        for path in args:
            if len(path) > 0 and path[0] == "/": path = path[1:]
            paths.append(path)
        return "/".join(paths)

    def base(self, *args):
        if len(args) == 0:
            return self._base
        path = self._path(*args)
        return urllib.parse.urljoin(self._base + "/", path)

    def ide(self, *args):
        if len(args) == 0: 
            return self._ide
        path = self._path(*args)
        return urllib.parse.urljoin(self._ide + "/", path)

    def asset(self, *args):
        if len(args) == 0: return self._asset
        path = self._path(*args)
        return urllib.parse.urljoin(self._asset + "/", path)
