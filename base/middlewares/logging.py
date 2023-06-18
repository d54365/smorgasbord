import time

from loguru import logger
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

from base.auth.backends import JWTAuthentication
from base.utils.header import HeaderUtil


class LoggingMiddleware:
    def __init__(self, get_response=None):
        self.get_response = get_response
        self.sensitive_headers = ("Authorization", "Proxy-Authorization")
        self.max_body_length = 50000

    def __call__(self, request):
        response = None
        cached_request_body = request.body
        start_time = int(time.time() * 1000)

        if hasattr(self, "process_request"):
            response = self.process_request(request)
        if not response:
            response = self.get_response(request)
        if hasattr(self, "process_response"):
            response = self.process_response(request, response)

        query_params = {}
        for k in request.GET.keys():
            query_params[k] = request.GET.getlist(k)

        end_time = int(time.time() * 1000)

        jwt_auth = JWTAuthentication()
        try:
            user_id, __ = jwt_auth.get_user_id_and_token(request)
        except AuthenticationFailed:
            user_id = None
        except TokenError:
            user_id = None
        except InvalidToken:
            user_id = None

        data = {
            "full_path": request.get_full_path(),
            "request_method": request.method,
            "ip": HeaderUtil.get_client_ip(request),
            "user_id": user_id,
            "headers": self._log_request_headers(request),
            "query_params": query_params,
            "body": cached_request_body,
            "status_code": response.status_code,
            "response": response.content.decode() if response.status_code in range(400, 500) else None,
            "response_headers": response.headers,
            "start_time": start_time,
            "end_time": end_time,
            "duration": end_time - start_time,
        }

        if response.status_code in range(400, 500):
            logger.error({"type": "[REQUEST]", **data})
        else:
            logger.info({"type": "[REQUEST]", **data})

        return response

    def _log_request_headers(self, request):
        return {k: v if k not in self.sensitive_headers else "*****" for k, v in request.headers.items()}

    def _chunked_to_max(self, msg):
        return msg[0 : self.max_body_length]  # noqa
