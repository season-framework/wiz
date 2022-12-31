def acl(wiz):
    ip = wiz.request.ip()
    
    ## uncomment this after set your environment
    # if ip not in ['127.0.0.1']:
    #     wiz.response.abort(401)
