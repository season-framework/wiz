config = wiz.model("portal/season/config")
BASEURI = config.auth_baseuri
LOGOUT_URI = config.auth_logout_uri
LOGIN_URL = config.auth_login_uri

if wiz.request.match(f"{BASEURI}/check") is not None:
    status = False if wiz.session.user_id() is None else True
    data = wiz.session.get()
    wiz.response.status(200, status=status, session=data)

if wiz.request.match(f"{BASEURI}/logout") is not None:
    returnTo = wiz.request.query("returnTo", "/")
    wiz.session.set(returnTo=returnTo)

    if LOGOUT_URI is not None and LOGOUT_URI != f"{BASEURI}/logout":
        wiz.response.redirect(LOGOUT_URI)

    authType = wiz.session.get("authType", "local")
    if authType == 'saml':
        wiz.response.redirect(f"{BASEURI}/saml/logout")

    wiz.session.clear()
    wiz.response.redirect(returnTo)

if wiz.request.match(f"{BASEURI}/login") is not None:
    if LOGIN_URL is not None and LOGIN_URL != f"{BASEURI}/login":
        wiz.response.redirect(LOGIN_URL)

if config.auth_saml_use:
    wiz.model("portal/season/auth/saml").proceed()

wiz.response.redirect("/")