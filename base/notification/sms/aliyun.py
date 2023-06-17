import uuid

from aliyunsdkcore.acs_exception.exceptions import ServerException, ClientException
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from django.conf import settings
from loguru import logger

from .base import SMSSender


class AliyunSMSSender(SMSSender):
    def __init__(self, access_key, secret, domain, region):
        super().__init__(access_key, secret, domain, region)
        self._client = AcsClient(self._access_key, self._secret)

    def send(self, sign_name, mobile, template, params):
        uid = uuid.uuid4().hex
        kwargs = {"sign_name": sign_name, "mobile": mobile, "params": params, "template": template}
        logger.info({"type": "[SMS]", "id": uid, "kwargs": kwargs})
        if mobile in settings.SMS_TEST_PHONES:
            return True
        request = self.make_request(**kwargs)
        try:
            response = self._client.do_action_with_exception(request)
        except ServerException as e:
            logger.error({"type": "[SMS]", "id": uid, "error": str(e)})
            return False
        except ClientException as e:
            logger.error({"type": "[SMS]", "id": uid, "error": str(e)})
            return False
        logger.info({"type": "[SMS]", "id": uid, "response": response})
        return True

    def make_request(self, mobile, sign_name, template, params):
        request = CommonRequest()
        request.set_accept_format("json")
        request.set_domain(self._domain)
        request.set_method("POST")
        request.set_protocol_type("https")
        request.set_version("2017-05-25")
        request.set_action_name("SendSms")
        request.add_query_param("RegionId", self._region)
        request.add_query_param("PhoneNumbers", mobile)
        request.add_query_param("SignName", sign_name)
        request.add_query_param("TemplateCode", template)
        request.add_query_param("TemplateParam", params)
        return request
