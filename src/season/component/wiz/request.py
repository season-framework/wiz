from season.component.base.request import Request as Base

class Request(Base):
    def __init__(self, wiz):
        super().__init__(wiz)
        
    def uri(self):
        return self.request().path
