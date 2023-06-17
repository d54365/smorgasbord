from django.core.mail import EmailMessage
from loguru import logger


class EmailSender:
    def __init__(self, subject, body, from_email, recipient: list or tuple):
        """
        subject: 邮件的主题
        body: 邮箱内容, 纯文本
        from_email: 发件人地址
        recipient: 收件人地址
        """
        self.email = EmailMessage(subject=subject, body=body, from_email=from_email, to=recipient)

    def set_bcc(self, bcc: list or tuple):
        """设置密送对象"""
        self.email.bcc = bcc

    def add_attachment(self, attachment):
        """添加附件"""
        self.email.attachments.append(attachment)

    def set_cc(self, cc: list or tuple):
        """设置抄送人"""
        self.email.cc = cc

    def set_headers(self, headers: dict):
        """设置邮件中额外的头信息"""
        self.email.extra_headers = headers

    def set_reply_to(self, reply_to: list or tuple):
        self.email.reply_to = reply_to

    def set_content_subtype_html(self):
        self.email.content_subtype = "html"

    def send(self):
        kwargs = {
            "subject": self.email.subject,
            "body": self.email.body,
            "from_email": self.email.from_email,
            "to": self.email.to,
            "bcc": self.email.bcc,
            "attachments": self.email.attachments,
            "headers": self.email.extra_headers,
            "cc": self.email.cc,
            "reply_to": self.email.reply_to,
            "type": "[EMAIL]",
        }
        try:
            ret = self.email.send()
            logger.info({**kwargs, "ret": ret})
        except Exception as e:
            logger.error({**kwargs, "error": e})
