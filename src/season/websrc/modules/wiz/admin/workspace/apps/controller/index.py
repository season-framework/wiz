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

WIZ_JS = """let wiz_controller = async ($sce, $scope, $timeout) => {
    // call wiz api
    let status = await wiz.API.async('status', {});
    console.log(status);

    /*
    // WIZ JS API Variables
    wiz.id // random generated wiz workspace app id
    wiz.namespace // defined namespace at view
    wiz.app_namespace // defined namespace at wiz workspace 
    wiz.render_id // random generated view instance id
    */

    /*
    // bind event. allow access form another wiz
    wiz.bind("modal-show", (data) => {
        $scope.data = data;
        $('#' + wiz.render_id).modal("show");
        $timeout();
    });

    // response to caller, when event end.
    $scope.event = {};
    $scope.event.submit = async () => {
        $('#' + wiz.render_id).modal("hide");
        let resp = true;
        wiz.response("modal-show", resp);
    }

    $scope.event.close = async () => {
        $('#' + wiz.render_id).modal("hide");
        let resp = false;
        wiz.response("modal-show", resp);
    }
    */

    // call another wiz's event.
    /*
    $scope.call_view = async () => {
        let resp = await wiz.connect("view namespace")
            .data({
                title: "Confirm",
                message: "Are you sure?",
                btn_close: "Cancel",
                btn_action: "Confirm",
                btn_class: "btn-success"
            })
            .event("modal-show");

        console.log("[response]", resp);
    }
    */

    /*
    let socket = wiz.socket.get();
    // let socket = wiz.socket.get('app_namespace');
    
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
    # framework.response.status(200, hello='hello', world='world')
"""

WIZ_PUG = """.container
    h3= message
    // {$ wiz.render("app-namespace-1", "view-instance-namespace") $}
    // {$ wiz.render("app-namespace-2", data='hello') $}
"""

WIZ_SOCKET = """# import datetime

# class Controller:
#     def __init__(self, wiz):
#         print("master")
#         self.cache = wiz.cache
#         self.room = "public"
        
#     def join(self, wiz, data):
#         wiz.flask_socketio.join_room(self.room, namespace=wiz.socket.namespace)
#         msg = dict()
#         msg["type"] = "init"
#         msg["data"] = self.cache.get("message", [])
#         wiz.socket.emit("message", msg, to=self.room, broadcast=True)

#     def message(self, wiz, data):
#         message = data["message"]
#         user_id = wiz.lib.util.randomstring(6)
#         msg = dict()
#         msg["type"] = "message"
#         msg["user"] = user_id
#         msg["message"] = message
#         msg["time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         with self.cache.open("message", []) as cache:
#             try:
#                 cache['message'].append(msg)
#                 cache['message'] = cache['message'][-100:]
#             except:
#                 cache['message'] = []
#                 cache['message'].append(msg)
#                 cache['message'] = cache['message'][-100:]

#         wiz.socket.emit("message", msg, to=self.room)
    
#     def connect(self, wiz, data):
#         pass

#     def disconnect(self, wiz, data):            
#         msg = dict()
#         msg["type"] = "users"
#         wiz.socket.emit("message", msg, to=self.room, broadcast=True)
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

        if app_id == 'new':
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
            info["socketio"] = WIZ_SOCKET
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
        elif info is None:
            framework.response.redirect("list")

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
