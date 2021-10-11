import season
import datetime

WIZ_JS = """var wiz_controller = function ($sce, $scope, $timeout) {
    // call api
    wiz.API.function('status', {}, function(res) {
        console.log(res);
    });

    // bind event. allow access form another wiz
    /*
    // response to caller, when event end.
    $scope.myevent = function() {
        var data = "hello";
        $scope.wiz_callback(data);
    };

    wiz.bind("event-name", function (data, callback) {
        $scope.wiz_callback = callback;
    });
    */

    // call another wiz's event.
    /*
    wiz.connect("wiz-namespace")
        // set data to send
        .data({ title: "My Title" }) 
        // call event and get response
        .event("event-name", function (data) {
            $scope.data = data;
            $timeout();
        });
    */
}
"""

WIZ_API = """def __startup__(framework):
    # TODO: Setup Access Level, etc.
    pass

def status(framework):
    # build response
    framework.response.status(200, 'hello')
"""

WIZ_KWARGS = """# use framework controller
# controller = season.interfaces.controller.admin.view()
# controller.__startup__(framework)

# TODO: Setup Access Level
if 'id' not in framework.session:
    framework.response.abort(401)

# use segments
# Route: /board/<category>/list
# View URI: /board/notice/list
segment = framework.request.segment
framework.log(segment)

# TODO: Build view variables
kwargs['message'] = "Hello, World!"
"""

WIZ_PUG = """.container
    h3= message
"""

class Controller(season.interfaces.wiz.controller.base):

    def __startup__(self, framework):
        super().__startup__(framework)
        self.css('css/main.less')
        if self.config.acl is not None: self.config.acl(framework)

    def __default__(self, framework):
        response = framework.response
        return response.redirect('list')

    def list(self, framework):
        if 'topmenus' in self.config: self.topnav(self.config.topmenus)

        cate = framework.request.segment.get(0, None)
        self.js('js/list.js')
        search = framework.request.query()
        if cate is not None:
            search['category'] = cate

        menus = [{"title":"ALL", "url": '/wiz/widget/list', 'pattern': r'^/wiz/widget/list$' }]
        category = ['widget', 'page']
        try:
            category = self.config.category
        except:
            pass
        for c in category:
            if type(c) == str:
                menus.append({ 'title': c, 'url': f'/wiz/widget/list/{c}' , 'pattern': r'^/wiz/widget/list/' + c + "$" })
            else:
                ctitle = c['title']
                c = c['id']
                menus.append({ 'title': ctitle, 'url': f'/wiz/widget/list/{c}' , 'pattern': r'^/wiz/widget/list/' + c + "$" })
        
        self.nav(menus)

        self.exportjs(search=search)
        return framework.response.render('list.pug', category=cate)

    def editor(self, framework):
        self.js('js/editor.js')
        self.css('css/editor.css')
        
        app_id = framework.request.segment.get(0, True)
        info = self.db.get(id=app_id)

        category = ['widget', 'page']
        try:
            category = self.config.category
        except:
            pass
        cate = framework.request.query("category", category[0])

        theme = season.stdClass()
        try:
            theme = self.config.theme
        except:
            pass

        if 'default' not in theme:
            theme.default = season.stdClass()
            theme.default.module = "wiz/theme"
            theme.default.view = "layout-wiz.pug"

        if info is None:
            info = dict()
            info["title"] = "New Widget"
            info["category"] = cate
            try:
                info["user_id"] = self.config.uid(framework)
            except:
                info["user_id"] = "unknown"
            newid = framework.lib.util.randomstring(32)
            res = self.db.get(id=newid)
            while res is not None:
                newid = framework.lib.util.randomstring(32)
                res = self.db.get(id=newid)
            info["id"] = newid
            info["namespace"] = newid
            info["created"] = datetime.datetime.now()
            info["kwargs"] = WIZ_KWARGS
            info["viewuri"] = ""
            info["route"] = ""
            info["html"] = WIZ_PUG
            info["js"] = WIZ_JS
            info["css"] = ""
            info["api"] = WIZ_API
            self.db.insert(info)
            framework.response.redirect("editor/" + newid)
        
        thememodule = None
        if 'thememodule' in self.config:
            thememodule = self.config.thememodule
        self.exportjs(app_id=app_id, category=category, theme=theme, thememodule=thememodule)
        framework.response.render('editor.pug', category=category, theme=theme)
