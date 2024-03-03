import season

segment = wiz.request.match(wiz.uri.ide("api/<id>/<function>/<path:path>"))

if segment is not None:
    App = wiz.ide.plugin.model("app")()
    app_id = segment.id
    function = segment.function

    fn = App.api(app_id)
    
    if fn is not None and function in fn:
        season.util.compiler(fn[function]).call(wiz=wiz, segment=segment)

    wiz.response.status(404)

Route = wiz.ide.plugin.model("route")()
route, segment = Route.match(wiz.request.uri())

if route.is_instance():
    route.proceed()
