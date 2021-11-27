import season

class Controller(season.interfaces.wiz.ctrl.admin.plugin.api):

    def __startup__(self, framework):
        super().__startup__(framework)

    def __default__(self, framework):
        plugin_id = framework.request.segment.get(0, True)
        bundle_id = framework.request.segment.get(1, True)
        fnname = framework.request.segment.get(2, True)

        plugin = self.plugin.instance(plugin_id)
        plugin.api(bundle_id, fnname)

        framework.response.status(500)