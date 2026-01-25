openai_key = "GPT KEY"
openai_model = "gpt-4o" 
assistant_guide = "소스코드 작성시에는 탭사이즈는 4로 만들어줘. pug 작성시에는 body 하위 코드만 작성해줘."

def acl(wiz):
    ip = wiz.request.ip()
    
    ## uncomment this after set your environment
    # if ip not in ['127.0.0.1']:
    #     wiz.response.abort(401)
