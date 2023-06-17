from celery import shared_task
from django.conf import settings

from base.notification.sms import sms_client


@shared_task
def send_sms_code(mobile, code):
    sms_client.send(settings.ALIYUN_SMS_SIGN_NAME, mobile, settings.ALIYUN_SMS_TEMPLATE_CODE, {"code": code})
