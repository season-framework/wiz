from season.core.component.base.response import Response as Base

class Response(Base):
    def __init__(self, wiz):
        super().__init__(wiz)
    
    def redirect(self, url):
        url = self.wiz.uri.base(url)
        self.status_code = 302
        resp = self._flask.redirect(url)
        return self._build(resp)