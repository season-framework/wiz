openai_key = "GPT KEY"
openai_model = "gpt-4o" 
assistant_guide = "소스코드 작성시에는 탭사이즈는 4로 만들어줘. pug 작성시에는 body 하위 코드만 작성해줘."

def acl(wiz):
    pass
    # try:
    #     session = wiz.model("portal/season/session").use()
    #     if session.get("role") == "admin":
    #         return True
    # except:
    #     pass

    # req_ip = wiz.request.ip()
    # if "," in req_ip: req_ip = req_ip.split(",")[0]
    # try:
    #     if req_ip in ['220.82.71.125', '127.0.0.1']:
    #         return True
    # except Exception as e:
    #     pass

    # wiz.response.abort(401)
