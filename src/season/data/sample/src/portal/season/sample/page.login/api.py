db = wiz.model("portal/season/orm").use("users")

def login():
    mail = wiz.request.query("mail", True)
    password = wiz.request.query("password", True)
    user = db.get(mail=mail)
    if user is None:
        wiz.response.status(401, "이메일 또는 비밀번호를 확인해주세요")
    if user['password'](password) == False:
        wiz.response.status(401, "이메일 또는 비밀번호를 확인해주세요")
    del user['password']
    wiz.session.set(**user)
    wiz.response.status(200, True)