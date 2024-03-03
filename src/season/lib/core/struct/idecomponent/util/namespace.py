class Namespace:
    @staticmethod
    def componentName(namespace):
        app_id_split = namespace.split(".")
        componentname = []
        for wsappname in app_id_split:
            componentname.append(wsappname.capitalize())
        componentname = "".join(componentname)
        return componentname
    
    @staticmethod
    def selector(namespace):
        return "wiz-" + "-".join(namespace.split("."))