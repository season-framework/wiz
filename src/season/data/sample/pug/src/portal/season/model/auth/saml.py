import season
import os
import datetime
from urllib.parse import urlparse
from onelogin.saml2.auth import OneLogin_Saml2_Auth

config = wiz.model("portal/season/config")
session = wiz.model("portal/season/session")

BASEURI = config.auth_baseuri
SAML_ENTITY = config.auth_saml_entity
SAML_BASE_PATH = config.auth_saml_base_path
SAML_ACS = config.auth_saml_acs
SAML_ERROR = config.auth_saml_error_uri

class SAML:
    def __init__(self):
        self.basepath = BASEURI

    def __call__(self):
        def build_auth(entity):
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

            basepath = wiz.project.path(os.path.join(SAML_BASE_PATH, entity))
            return OneLogin_Saml2_Auth(req, custom_base_path=basepath)

        pattern = self.basepath + "/saml/<action>/<entity>/<path:path>"
        segment = wiz.request.match(pattern)

        if segment is None:
            return
        
        entity = SAML_ENTITY
        if wiz.session.get("ENTITY", None) is not None:
            entity = wiz.session.get("ENTITY", None)
        if 'entity' in segment and segment.entity is not None:
            entity = segment.entity

        self.__auth__ = build_auth(entity)
        self.__ENTITY__ = entity

        action = segment.action
        if action is None:
            return
        fn = None
        if hasattr(self, action):
            fn = getattr(self, action)
        if fn is None:
            return
        fn()
    
    def proceed(self):
        self.__call__()

    def login(self):
        auth = self.__auth__
        if session.user_id() is not None:
            wiz.response.redirect("/")
        redirect = wiz.request.query('redirect', '/')
        session.set(AuthNRequestID=auth.get_last_request_id(), SAML_REDIRECT=redirect, ENTITY=self.__ENTITY__)
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
                compiler = season.util.compiler(SAML_ACS)
                sessiondata = compiler.call(wiz=wiz, userinfo=userinfo)
            
            redirect = session.get('SAML_REDIRECT', None)
            try:
                session.delete('SAML_REDIRECT')
            except:
                pass
            if redirect is None:
                redirect = wiz.request.query('RelayState', "/")

            sessiondata['samlNameId'] = auth.get_nameid()
            sessiondata['samlNameIdFormat'] = auth.get_nameid_format()
            sessiondata['samlNameIdNameQualifier'] = auth.get_nameid_nq()
            sessiondata['samlNameIdSPNameQualifier'] = auth.get_nameid_spnq()
            sessiondata['samlSessionIndex'] = auth.get_session_index()
            sessiondata['authType'] = 'saml'

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
        returnTo = session.get('returnTo', "/")

        session.clear()
        url = auth.process_slo(request_id=request_id)

        errors = auth.get_errors()
        if len(errors) == 0:
            if url is not None:
                wiz.response.redirect(url)
        elif auth.get_settings().is_debug_active():
            auth.get_last_error_reason()

        wiz.response.redirect(returnTo)
    
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

Model = SAML()
