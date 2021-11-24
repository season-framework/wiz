def process(framework):
    framework.wiz = framework.model("wiz", module="wiz").use()
    framework.response.data.set(wiz=framework.wiz)
    framework.wiz.route()
