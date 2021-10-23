import season
import datetime

WIZ_SOCKETAPI = """class Controller:
    def __init__(self, framework):
        # init something
        pass

    def __startup__(self, framework):
        # localized socket emit
        framework.socket.emit("startup /wiz socket")

        # global socket emit
        framework.socketio.emit("event name", "data", namespace="", to="")

        # use framework
        framework.session = framework.lib.session.to_dict()

    def response(self, framework, data):
        framework.socket.emit("hello world")"""

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

class Controller(season.interfaces.wiz.admin.base):

    def __startup__(self, framework):
        super().__startup__(framework)
        self.css('css/interface/main.less')

    def __default__(self, framework):
        self.js('js/interface/editor.js')
        self.css('css/interface/editor.css')
        
        app_id = framework.request.segment.get(0, True)
        info = self.db.get(id=app_id)

        category = ['widget', 'page']
        try:
            category = self.config.category
        except:
            pass
        cate = framework.request.query("category", category[0])

        theme = framework.model("wiz", module="wiz").themes()

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
            info["version"] = "master"
            info["version_name"] = "master"
            info["version_message"] = ""
            info["viewuri"] = ""
            info["route"] = ""
            info["html"] = WIZ_PUG
            info["js"] = WIZ_JS
            info["css"] = ""
            info["api"] = WIZ_API
            info["socketio"] = WIZ_SOCKETAPI
            self.db.insert(info)
            framework.response.redirect("editor/" + newid)
        
        self.exportjs(app_id=app_id, category=category, theme=theme)
        framework.response.render('interface/editor.pug', category=category, theme=theme)
