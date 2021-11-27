def process(framework):
    framework.wiz = framework.model("wiz", module="wiz").use()
    framework.response.data.set(wiz=framework.wiz)
    framework.wiz.route()

    request_uri = framework.request.uri()
    if request_uri.startswith("/wiz/admin"):
        if request_uri.startswith("/wiz/admin/api/") == False and request_uri.startswith("/wiz/admin/plugin/") == False:
            plugin = framework.model("plugin", module="wiz")
            plugin.route()