import season
import os
import datetime
from urllib.parse import urlparse
from onelogin.saml2.auth import OneLogin_Saml2_Auth

SAML_ENTITY = wiz.config("season").get("saml_entity", "season")
SAML_BASE_PATH = wiz.config("season").get("saml_base_path", "config/auth/saml")
SAML_ACS = wiz.config("season").get("saml_acs", None)
SAML_ERROR = wiz.config("season").get("saml_error", "/")

session = wiz.model("portal/season/session").use()

class Model:
    def __init__(self):
        self.basepath = '/auth'

    @classmethod
    def baseuri(cls, basepath='/auth'):
        return cls()()

    def __call__(self):
        def build_auth(entity=SAML_ENTITY):
            request = wiz.request.request()
            url_data = urlparse(request.url)
            req = {
                'https': 'on',
                'http_host': request.host,
                'server_port': url_data.port,
                'script_name': request.path,
                'get_data': request.args.copy(),
                'post_data': request.form.copy(),
                'query_string': request.query_string
            }

            basepath = wiz.branch.path(os.path.join(SAML_BASE_PATH, entity))
            return OneLogin_Saml2_Auth(req, custom_base_path=basepath)

        self.__auth__ = build_auth()
        pattern = self.basepath + "/saml/<action>/<path:path>"
        segment = wiz.request.match(pattern)

        if segment is None:
            return
        action = segment.action
        if action is None:
            return
        fn = None
        if hasattr(self, action):
            fn = getattr(self, action)
        if fn is None:
            return
        fn()

    def login(self):
        auth = self.__auth__
        if session.has("id"):
            wiz.response.redirect("/")
        redirect = wiz.request.query('redirect', '/')
        session.set(AuthNRequestID=auth.get_last_request_id(), SAML_REDIRECT=redirect)
        url = auth.login()
        wiz.response.redirect(url)

    def acs(self):
        auth = self.__auth__
        request_id = session.get('AuthNRequestID', None)
        auth.process_response(request_id=request_id)
        errors = auth.get_errors()
        error_reason = auth.get_last_error_reason()

        if len(errors) == 0:
            if request_id is not None:
                session.delete('AuthNRequestID')
            
            userinfo = auth.get_attributes()
            sessiondata = dict()
            if SAML_ACS is not None:
                sessiondata = SAML_ACS(userinfo)
    
            redirect = wiz.request.query('RelayState', None)
            if redirect is None:
                redirect = session.get('SAML_REDIRECT', '/')
            session.delete('SAML_REDIRECT')

            sessiondata['samlNameId'] = auth.get_nameid()
            sessiondata['samlNameIdFormat'] = auth.get_nameid_format()
            sessiondata['samlNameIdNameQualifier'] = auth.get_nameid_nq()
            sessiondata['samlNameIdSPNameQualifier'] = auth.get_nameid_spnq()
            sessiondata['samlSessionIndex'] = auth.get_session_index()

            istoken = session.get("istoken", None)
            if istoken == True:
                token = wiz.model("model/token").generate(sessiondata['id'])
                sessiondata['token'] = token
                session.delete("istoken")
            session.set(**sessiondata)
            wiz.response.redirect(redirect)
        
        wiz.response.redirect(SAML_ERROR)

    def logout(self):
        auth = self.__auth__
        name_id = session.get('samlNameId', None)
        name_id_format = session.get('samlNameIdFormat', None)
        name_id_nq = session.get('samlNameIdNameQualifier', None)
        name_id_spnq = session.get('samlNameIdSPNameQualifier', None)
        session_index = session.get('samlSessionIndex', None)
        wiz.response.redirect(auth.logout(name_id=name_id, session_index=session_index, nq=name_id_nq, name_id_format=name_id_format, spnq=name_id_spnq))
    
    def sls(self):
        auth = self.__auth__
        request_id = session.get('LogoutRequestID', None)

        session.clear()
        url = auth.process_slo(request_id=request_id)

        errors = auth.get_errors()
        if len(errors) == 0:
            if url is not None:
                wiz.response.redirect(url)
        elif auth.get_settings().is_debug_active():
            auth.get_last_error_reason()
        wiz.response.redirect('/')
    
    def metadata(self):
        auth = self.__auth__
        settings = auth.get_settings()
        metadata = settings.get_sp_metadata()
        errors = settings.validate_metadata(metadata)
        
        if len(errors) == 0:
            metadata = metadata.decode('utf-8')
            wiz.response.send(metadata, content_type='text/xml')
        else:
            wiz.response.send(', '.join(errors))
