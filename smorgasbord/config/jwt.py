from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),  # 指定token有效期
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),  # 指定token刷新有效期
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHMS": ["HS256"],  # 指定加密的哈希函数
    "VERIFY_SIGNATURE": True,  # 开启验证密钥
    "VERIFY_EXP": True,  # 开启验证token是否过期
    "AUDIENCE": None,
    "ISSUER": "https://drw.com",
    "LEEWAY": 0,
    "REQUIRE": ["exp"],
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
}
