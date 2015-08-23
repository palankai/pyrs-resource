"""
This module contains the default configurations.
The :py:class:`pyrs.resource.base.App` config will be based on these values.
"""
#: This option will be used for decorators.
#: Usage `getattr(func, conf.decorate)`
decorate = '_endpoint'

#: Default host for the application
host = 'localhost'

#: You can get more information in response
#: like traceback and args of exception
debug = False

body_schema_option = 'request'

#: Enable/disable injecting the :py:class:`.base.App` as keyword argument
inject_app = False

#: Name used for app injection
inject_app_name = 'app'

#: Enable/disable injecting the :py:attr:`.request.auth` as keyword argument
inject_auth = False

#: With this name the auth will be injected
inject_auth_name = 'auth'

#: Enable/disable injecting the request body
inject_body = True

#: Enable/disable injecting the cookies
inject_cookies = False

#: With this name the cookies will be injected
inject_cookies_name = 'cookies'

#: Enable/disable injecting the path arguments
#: If a name provided the path arguments will be injected as specified
inject_path = True

#: Enable/disable injecting the query arguments
#: If a name provided the query arguments will be injected as specified
inject_query = True


inject_request = False
inject_request_name = 'request'
inject_session = False
inject_session_name = 'session'
query_schema_option = 'query'
option_status = 200
option_status_name = 'status'
option_headers_name = 'headers'
option_response_name = 'response'
