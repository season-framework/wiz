import season
import os
import datetime
import urllib
from urllib.parse import urlparse

from oic.oic import Client
from oic.utils.authn.client import CLIENT_AUTHN_METHOD
from oic.oic.message import ProviderConfigurationResponse
from oic.oic.message import RegistrationResponse
from oic import rndstr
from oic.utils.http_util import Redirect
from oic.oic.message import AuthorizationResponse

config = wiz.model("portal/season/config")
session = wiz.model("portal/season/session")
BASEURI = config.auth_baseuri
orm = wiz.model("portal/season/orm")

class OIDC:
    def __init__(self):
        self.basepath = BASEURI

    def __call__(self):
        pattern = self.basepath + "/oidc/<action>/<issuer>/<path:path>"
        segment = wiz.request.match(pattern)
        
        action = segment.action
        if action is None:
            return

        fn = None
        if hasattr(self, action):
            fn = getattr(self, action)
            client = Client(client_authn_method=CLIENT_AUTHN_METHOD)

            idpdb = orm.use("trust/idp")
            oidcdb = orm.use("trust/oidc/opwellknown")
            issuer = segment.issuer

            if issuer is None:
                issuer = session.get('issuer')

            if issuer is not None:
                session.set(issuer=issuer)

            issuer = idpdb.get(id=issuer)
            if issuer is None:
                return
            issuer = issuer['key']
            op_info = oidcdb.get(issuer=issuer)
            del op_info['wellknown']

            op_info = ProviderConfigurationResponse(version="1.0", **op_info)
            client.handle_provider_config(op_info, op_info['issuer'])

            info = {"client_id": op_info['client_id'], "client_secret": op_info['secret']}
            client_reg = RegistrationResponse(**info)
            client.store_registration_info(client_reg)
            client.redirect_uris.append("https://proxy.kafe.seasonsoft.net/auth/oidc/callback")
            client.registration_response["redirect_uris"] = ["https://proxy.kafe.seasonsoft.net/auth/oidc/callback"]

            self.client = client
            fn()

    def proceed(self):
        self.__call__()

    def login(self):
        client = self.client
        session.set(state=rndstr(), nonce=rndstr())
        args = {
            "client_id": client.client_id,
            "response_type": "code",
            "scope": ["openid", "email", "profile"],
            "nonce": session.get("nonce"),
            "redirect_uri": client.registration_response["redirect_uris"][0],
            "state": session.get("state")
        }
        auth_req = client.construct_AuthorizationRequest(request_args=args)
        login_url = auth_req.request(client.authorization_endpoint)
        wiz.response.redirect(login_url)

    def callback(self):
        client = self.client
        query = wiz.request.query()
        query = urllib.parse.urlencode(query)

        print("Test")

        aresp = client.parse_response(AuthorizationResponse, info=query, sformat="urlencoded")        
        args = {"code": aresp["code"]}
        resp = client.do_access_token_request(state=aresp["state"], request_args=args, authn_method="client_secret_basic")
        userinfo = client.do_user_info_request(state=aresp["state"])

        print(userinfo)

        wiz.response.status(200, userinfo)

Model = OIDC()