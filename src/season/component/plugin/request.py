from season.component.base.request import Request as Base

class Request(Base):
    def __init__(self, wiz):
        super().__init__(wiz)
        
    def uri(self):
        wizurl = self.wiz.baseurl
        if self.wiz.id is not None:
            wizurl = wizurl + "/ui/" + self.wiz.id
        return self.request().path[len(wizurl):]
