import time

from celery import shared_task
from django.conf import settings
from django.core.cache import cache
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from itsdangerous import URLSafeSerializer

from base.constants.cache import CacheConstants
from base.notification.email import EmailSender


@shared_task
def send_email_active(user_id, user_mail):
    title = _("Email activation verification email")

    url_safe_serializer = URLSafeSerializer(settings.SECRET_KEY)
    token = url_safe_serializer.dumps({"user_id": user_id, "mail": user_mail, "ts": time.time()})

    content_rsp = render(
        None, "emai_active.html", {"url": f"{settings.HOST}/activate/{token}"}, content_type="application/xhtml+xml"
    )
    content = str(content_rsp.content, encoding="utf-8")
    email_sender = EmailSender(title, content, None, [user_mail])
    email_sender.set_content_subtype_html()
    email_sender.send()

    cache.set(
        CacheConstants.EMAIL_ACTIVE.format(user_id=user_id),
        f"{token}_{int(time.time())}",
        CacheConstants.EMAIL_ACTIVE_EXPIRED,
    )

    # 每发送一次+1, 避免24小时内发送多次, 24小时内最多发送5次
    limit_key = CacheConstants.EMAIL_ACTIVE_LIMIT.format(user_id=user_id)
    limit_value = cache.get(limit_key)
    if limit_value is None:
        limit_value = 0
    limit_value += 1
    cache.set(limit_value, limit_value, CacheConstants.EMAIL_ACTIVE_LIMIT_EXPIRED)
