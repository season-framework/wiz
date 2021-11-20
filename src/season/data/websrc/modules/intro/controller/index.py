import season
import random

class Controller(season.interfaces.controller.base):

    def __init__(self, framework):
        super().__init__(framework)

    def __default__(self, framework):
        return self.redirect('list')

    def list(self, framework): 
        data = []
        for i in range(20):
            data.append({
                'id': 'item-' + str(i+1),
                'title' :'Title #{}'.format(i+1), 
                'value1': random.randint(0, 1000),
                'value2': random.randint(0, 1000),
                'value3': random.randint(0, 10000) / 100
                })
        return framework.response.render('list.pug', data=data)

    def item(self, framework):
        message = framework.model('data').getMessage()
        itemid = framework.request.segment.get(0, True)
        return framework.response.render('item.pug', id=itemid, message=message)