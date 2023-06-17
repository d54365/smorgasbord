from django.conf import settings

from .aliyun import AliyunSMSSender

sms_client = AliyunSMSSender(
    settings.ALIYUN_SMS_ACCESS_KEY, settings.ALIYUN_SMS_SECRET, settings.ALIYUN_SMS_DOMAIN, settings.ALIYUN_SMS_REGION
)
