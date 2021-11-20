import season
import time

WIZ_CONTROLLER = """### get request query
### wiz.request.query(<KEY>, <DEFAULT_VALUE>)
# data = wiz.request.query() # get all queries as dict type
# value = wiz.request.query("key", "test") # get `key` value, if not exist in query, return default value
# value = wiz.request.query("key", True) # if default value is True, this key required

### load text from dictionary
# hello = dic("hello")
# title = dic("title.text")

### use selected controller
# controller.custom_function()

### use segments
### Route: /board/<category>/list
### View URI: /board/notice/list
# segment = framework.request.segment

### Build view variables, you can use
# kwargs['message'] = "Hello, World!"
"""

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

    /*
    var socket = wiz.socket.get();    
    socket.on("connect", function (data) {
        socket.emit("response", "hello");
    });

    socket.on("disconnect", function (data) {
    });

    socket.on("response", function (data) {
        console.log("response", data);
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

WIZ_PUG = """.container
    h3= message
"""

class Controller(season.interfaces.wiz.ctrl.admin.workspace.view):

    def __startup__(self, framework):
        super().__startup__(framework)
        self.css('main.less')
        
    def __default__(self, framework):
        framework.response.redirect("list")

    def list(self, framework):
        cate = framework.request.segment.get(0, None)
        self.js('list.js')
        framework.response.render('list.pug')

    def editor(self, framework):
        self.js('editor.js')
        self.js('/wiz/theme/editor/editor.js')
        self.css('editor.css')

        app_id = framework.request.segment.get(0, True)
        info = self.wiz.data.get(app_id, mode='app')

        if info is None:
            pkg = dict()
            pkg["id"] = framework.lib.util.randomstring(12) + str(int(time.time()))
            pkg["title"] = "New App"
            pkg["namespace"] = pkg["id"]
            pkg["properties"] = {"html": "pug", "js": "javascript", "css": "scss"}
            pkg["viewuri"] = ""

            info = dict()
            info["package"] = pkg
            info["controller"] = WIZ_CONTROLLER
            info["api"] = WIZ_API
            info["socketio"] = ""
            info["html"] = WIZ_PUG
            info["js"] = WIZ_JS
            info["css"] = ""
            info["dic"] = dict()
            info["dic"]["default"] = dict()
            info["dic"]["default"]["hello"] = "hello"
            info["dic"]["ko"] = dict()
            info["dic"]["ko"]["hello"] = "안녕하세요"

            self.wiz.data.update(info, mode='app')
            framework.response.redirect("editor/" + pkg["id"])

        controllers = framework.wiz.controllers()        
        themes = framework.wiz.themes()
        self.exportjs(APPID=app_id, CTRLS=controllers, THEMES=themes)
        framework.response.render('editor.pug')

    def preview(self, framework):
        app_id = framework.request.segment.get(0, True)
        framework.request.segment = season.stdClass()
        wiz = framework.wiz.instance()
        wiz.response.render(app_id)
        framework.response.status(200, app_id)
