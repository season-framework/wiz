import datetime
import re

orm = wiz.model("portal/season/orm")
userdb = orm.use("user")

def sendmail(user):
    # smtp = wiz.config('portal/season/smtp').data
    # smtp['title'] = '회원가입 인증메일'
    # smtp['to'] = mail
    # smtp['verify_code'] = verify_code
    # wiz.model('smtp').mail_to(**smtp)
    return wiz.response.status(200, True)

def check():
    mail = wiz.request.query('mail', True)
    if not re.match(r"[^@]+@[^@]+\.[^@]+", mail):
        return wiz.response.status(401, '잘못된 이메일 형식입니다.')

    user = userdb.get(mail=mail)

    # 이미 가입되있거나 가입 진행중인 경우
    if user is not None:
        if user['status'] == 'active':
            return wiz.response.status(401, '이미 가입된 이메일입니다.')
        elif user['status'] == 'inactive':
            return wiz.response.status(401, '비활성화된 계정입니다. 관리자에게 문의해주세요.')
        return wiz.response.status(200, True)

    # 회원가입 진행
    user = dict()
    user['mail'] = mail
    user['role'] = 'user'
    user['status'] = 'verify'
    user['code'] = orm.random(6, number=True)
    user['created'] = datetime.datetime.now()
    user['updated'] = datetime.datetime.now()

    userdb.insert(user)
    return sendmail(user)

def resend():
    mail = wiz.request.query('mail', True)
    if not re.match(r"[^@]+@[^@]+\.[^@]+", mail):
        return wiz.response.status(401, '잘못된 이메일 형식입니다.')

    user = userdb.get(mail=mail)

    # 회원 정보 확인
    if user is None:
        return wiz.response.status(404, "가입되지 않은 회원입니다.")
    if user['status'] == 'active':
        return wiz.response.status(401, '이미 가입된 이메일입니다.')
    elif user['status'] == 'inactive':
        return wiz.response.status(401, '비활성화된 계정입니다. 관리자에게 문의해주세요.')
    
    # 인증 코드 생성
    user['code'] = orm.random(6, number=True)
    userdb.update(user, mail=mail)
    return sendmail(user)

def verify():
    mail = wiz.request.query('mail', True)
    code = wiz.request.query('code', True)

    # 이메일 형식 확인
    if not re.match(r"[^@]+@[^@]+\.[^@]+", mail):
        return wiz.response.status(401, '잘못된 이메일 형식입니다.')

    # 사용자 정보 불러오기
    user = userdb.get(mail=mail)

    # 회원 정보 확인
    if user is None:
        return wiz.response.status(404, "가입되지 않은 회원입니다.")
    if user['status'] == 'active':
        return wiz.response.status(401, '이미 가입된 이메일입니다.')
    elif user['status'] == 'inactive':
        return wiz.response.status(401, '비활성화된 계정입니다. 관리자에게 문의해주세요.')

    if user['code'] == code:
        wiz.session.set(verified=mail)
        return wiz.response.status(200, True)

    return wiz.response.status(404, "잘못된 인증번호 입니다.")

def join():
    mail = wiz.request.query('mail', True)
    verified = wiz.session.get("verified")
    if verified != mail:
        return wiz.response.status(401, "잘못된 접근입니다")

    info = userdb.get(mail=mail)
    if info['status'] != 'verify':
        return wiz.response.status(401, "잘못된 접근입니다")

    user = wiz.request.query()
    user['updated'] = datetime.datetime.now()
    user['status'] = 'active'
    user['role'] = 'user'
    userdb.update(user, mail=mail)
    wiz.session.clear()
    return wiz.response.status(200, True)