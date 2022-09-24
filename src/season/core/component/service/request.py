from season.core.component.base.request import Request as Base

class Request(Base):
    def __init__(self, wiz):
        super().__init__(wiz)
        
    def uri(self):
        baseurl = self.wiz.uri.base()
        return self.request().path[len(baseurl):]
