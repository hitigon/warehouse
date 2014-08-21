#!/usr/bin/env python
#
# @name: oauth/validator.py
# @create: Aug. 9th, 2014
# @update: Aug. 21th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
import bcrypt
from utils import get_auth_base_uri, get_utc_time
from oauthlib.oauth2 import RequestValidator
from models.oauth.client import Client
from models.oauth.code import Code
from models.oauth.token import Token
from models.user import User


CODE_EXPIRE_TIME = 6000
#TOKEN_EXPIRE_TIME = 3600


class OAuth2Validator(RequestValidator):

    def validate_client_id(self, client_id, request, *args, **kwargs):
        client = Client.objects(client_id=client_id).first()
        return client is not None

    def validate_redirect_uri(self, client_id, redirect_uri, request,
                              *args, **kwargs):
        # Is the client allowed to use the supplied redirect_uri? i.e. has
        # the client previously registered this EXACT redirect uri.
        client = Client.objects(client_id=client_id).first()
        base_uri = get_auth_base_uri()
        if client:
            for uri in client.redirect_uris:
                if redirect_uri == base_uri + uri:
                    return True
        return False

    def get_default_redirect_uri(self, client_id, request, *args, **kwargs):
        # The redirect used if none has been supplied.
        # Prefer your clients to pre register a redirect uri rather than
        # supplying one on each authorization request.
        client = Client.objects(client_id=client_id).first()
        return get_auth_base_uri() + client.default_redirect_uri

    def validate_scopes(self, client_id, scopes, client, request,
                        *args, **kwargs):
        # Is the client allowed to access the requested scopes?
        if not scopes:
            scopes = client.default_scopes
        return True if set(client.scopes) & set(scopes) else False

    def get_default_scopes(self, client_id, request, *args, **kwargs):
        # Scopes a client will authorize for if none are supplied in the
        # authorization request.
        client = Client.objects(client_id=client_id).first()
        return client.default_scopes

    def validate_response_type(self, client_id, response_type, client, request,
                               *args, **kwargs):
        # Clients should only be allowed to use one type of response type, the
        # one associated with their one allowed grant type.
        # In this case it must be "code".
        client = Client.objects(client_id=client_id).first()
        return client.response_type == response_type

    def save_authorization_code(self, client_id, code, request,
                                *args, **kwargs):
        # Remember to associate it with request.scopes, request.redirect_uri
        # request.client, request.state and request.user (the last is passed in
        # post_authorization credentials, i.e. { 'user': request.user}.
        client = Client.objects(client_id=client_id).first()
        Code(client=client, user=request.user, state=request.state,
             code=code['code'], scopes=request.scopes,
             redirect_uri=request.redirect_uri,
             expires_at=get_utc_time(CODE_EXPIRE_TIME)).save()

    def authenticate_client(self, request, *args, **kwargs):
        # Whichever authentication method suits you, HTTP Basic might work
        client_id = request.client_id
        client = Client.objects(client_id=client_id).first()
        request.client = client
        return client is not None

    def authenticate_client_id(self, client_id, request, *args, **kwargs):
        # Don't allow public (non-authenticated) clients
        client = Client.objects(client_id=client_id).first()
        request.client = client
        return client is not None

    def validate_user(self, username, password, client, request,
                      *args, **kwargs):
        user = User.objects(username=username).first()
        if not user:
            return False
        pw = user.password.encode()
        request.user = user
        return pw == bcrypt.hashpw(password.encode(), pw)

    def validate_code(self, client_id, code, client, request, *args, **kwargs):
        # Validate the code belongs to the client. Add associated scopes,
        # state and user to request.scopes, request.state and request.user.
        client = Client.objects(client_id=client_id).first()
        client_code = Code.objects(client=client).first()
        valid = client_code.code == code
        if valid and client_code.expires_at > get_utc_time():
            request.scopes = client_code.scopes
            request.user = client_code.user
            request.state = client_code.state
            return True
        return False

    def confirm_redirect_uri(self, client_id, code, redirect_uri, client,
                             *args, **kwargs):
        # You did save the redirect uri with the authorization code right?
        c = Code.objects(code=code, client=client).first()
        uri = get_auth_base_uri() + redirect_uri
        return c.redirect_uri == redirect_uri or uri == c.redirect_uri

    def validate_grant_type(self, client_id, grant_type, client, request,
                            *args, **kwargs):
        # Clients should only be allowed to use one type of grant.
        # In this case, it must be "authorization_code" or "refresh_token"
        client = Client.objects(client_id=client_id).first()
        return client.grant_type == grant_type

    def save_bearer_token(self, token, request, *args, **kwargs):
        # Remember to associate it with request.scopes, request.user and
        # request.client. The two former will be set when you validate
        # the authorization code. Don't forget to save both the
        # access_token and the refresh_token and set expiration for the
        # access_token to now + expires_in seconds.
        Token(client=request.client, user=request.user,
              scopes=request.scopes, access_token=token['access_token'],
              refresh_token=token['refresh_token'],
              expires_at=get_utc_time(token['expires_in'])).save()
        return request.client.default_redirect_uri

    def invalidate_authorization_code(self, client_id, code, request,
                                      *args, **kwargs):
        # Authorization codes are use once, invalidate it when a Bearer token
        # has been acquired.
        Code.objects(code=code).delete()

    def validate_bearer_token(self, token, scopes, request):
        # Remember to check expiration and scope membership
        t = Token.objects(access_token=request.access_token).first()
        if t:
            valid = (set(t.scopes) & set(scopes))
            valid = valid and t.expires_at > get_utc_time()
            request.user = valid and t.user or None
            return valid
        return False

    def get_original_scopes(self, refresh_token, request, *args, **kwargs):
        # Obtain the token associated with the given refresh_token and
        # return its scopes, these will be passed on to the refreshed
        # access token if the client did not specify a scope during the
        # request.
        pass
