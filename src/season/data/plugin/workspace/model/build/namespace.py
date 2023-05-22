import season
import re

class Namespace:
    def componentName(self, namespace):
        app_id_split = namespace.split(".")
        componentname = []
        for wsappname in app_id_split:
            componentname.append(wsappname.capitalize())
        componentname = "".join(componentname)
        return componentname
    
    def selector(self, namespace):
        return "wiz-" + "-".join(namespace.split("."))

Model = Namespace()