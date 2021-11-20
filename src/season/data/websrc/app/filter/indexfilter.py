def ng(name):
    return '{{' + str(name) + '}}'

def process(framework):
    request_uri = framework.request.uri()

    if request_uri == '/':
        return framework.response.redirect("/intro")

    framework.response.data.set(ng=ng)

    framework.session = framework.lib.session.to_dict()
    framework.response.data.set(session=framework.session)
