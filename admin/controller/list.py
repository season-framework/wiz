import season

class Controller(season.interfaces.wiz.admin.base):

    def __startup__(self, framework):
        super().__startup__(framework)
        self.css('css/interface/main.less')
        
        menus = [{"title":"ALL", "url": '/wiz/admin/list', 'pattern': r'^/wiz/admin/list$' }]
        category = ['widget', 'page']
        try:
            category = self.config.category
        except:
            pass
        for c in category:
            if type(c) == str:
                menus.append({ 'title': c, 'url': f'/wiz/admin/list/{c}' , 'pattern': r'^/wiz/admin/list/' + c + "$" })
            else:
                ctitle = c['title']
                c = c['id']
                menus.append({ 'title': ctitle, 'url': f'/wiz/admin/list/{c}' , 'pattern': r'^/wiz/admin/list/' + c + "$" })
        self.subnav(menus)


    def __default__(self, framework):
        cate = framework.request.segment.get(0, None)
        self.js('js/interface/list.js')
        search = framework.request.query()
        if cate is not None:
            search['category'] = cate

        self.exportjs(search=search)
        return framework.response.render('interface/list.pug', category=cate)