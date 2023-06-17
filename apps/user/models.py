from django.contrib.auth.hashers import make_password, check_password, is_password_usable
from django.db import models

from base.utils.base_model import BaseModel


class AbstractBaseUser(models.Model):
    REQUIRED_FIELDS = []

    # Stores the raw password if set_password() is called so that it can
    # be passed to password_changed() after the model is saved.
    _password = None

    class Meta:
        abstract = True

    def __str__(self):
        return self.get_username()

    def get_username(self):
        """Return the username for this User."""
        return getattr(self, self.USERNAME_FIELD)  # noqa

    def clean(self):
        setattr(self, self.USERNAME_FIELD, self.normalize_username(self.get_username()))  # noqa

    def natural_key(self):
        return (self.get_username(),)

    @property
    def is_anonymous(self):
        """
        Always return False. This is a way of comparing User objects to
        anonymous user.
        """
        return False

    @property
    def is_authenticated(self):
        """
        Always return True. This is a way to tell if the user has been
        authenticated in templates.
        """
        return True

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self._password = raw_password

    def check_password(self, raw_password):
        """
        Return a boolean of whether the raw_password was correct. Handles
        hashing formats behind the scenes.
        """

        def setter(raw_password):
            self.set_password(raw_password)
            # Password hash upgrades shouldn"t be considered password changes.
            self._password = None
            self.save(update_fields=["password"])

        return check_password(raw_password, self.password, setter)

    def set_unusable_password(self):
        # Set a value that will never be a valid hash
        self.password = make_password(None)

    def has_usable_password(self):
        """
        Return False if set_unusable_password() has been called for this user.
        """
        return is_password_usable(self.password)


class User(AbstractBaseUser, BaseModel):
    class Identity(models.TextChoices):
        ADMIN = 0, "管理员"
        USER = 1, "普通用户"

    class Status(models.TextChoices):
        ENABLED = 0, "启用"
        DISABLED = 1, "禁用"

    username = models.CharField(max_length=32, verbose_name="用户名", unique=True)
    password = models.CharField(max_length=128, verbose_name="密码")
    mobile = models.CharField(max_length=32, verbose_name="手机号码", unique=True)
    mail = models.CharField(max_length=128, verbose_name="邮箱", null=True, default=None, unique=True)
    mail_active = models.BooleanField(verbose_name="邮箱验证状态", default=False)
    mail_active_at = models.DateTimeField(verbose_name="邮箱验证时间", null=True)
    identity = models.SmallIntegerField(choices=Identity.choices, verbose_name="身份, 0管理员, 1普通用户", default=Identity.USER)
    status = models.SmallIntegerField(choices=Status.choices, verbose_name="状态, 0启用, 1禁用", default=Status.ENABLED)
    last_login_at = models.DateTimeField(null=True, verbose_name="上次登陆时间")
    created = models.ForeignKey(
        "self",
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="创建人",
        related_name="user_created",
        db_constraint=False,
    )
    updated = models.ForeignKey(
        "self",
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="上次修改人",
        related_name="user_updated",
        db_constraint=False,
    )

    USERNAME_FIELD = "username"

    REQUIRED_FIELDS = []

    class Meta:
        db_table = "user_user"

    @property
    def is_admin(self):
        return self.identity == self.Identity.ADMIN

    @property
    def is_active(self):
        return self.status == int(self.Status.ENABLED.value)  # noqa
