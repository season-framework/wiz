from season.core.component.base.request import Request as Base

class Request(Base):
    def __init__(self, wiz):
        super().__init__(wiz)
        
    def uri(self):
        ideurl = self.wiz.uri.ide()
        return self.request().path[len(ideurl):]
