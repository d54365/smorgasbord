class CacheConstants:
    ID_GEN = "id_gen:worker"
    CACHE_DISK_STR = "disk"
    CACHE_LOCK_STR = "lock"
    USER_AGENT = "ua:{ua}"

    SMS_CODE = "account:sms_code:{mobile}"
    SMS_CODE_EXPIRED = 60 * 5

    USER_ACCESS_TOKEN = "user:access_token:{ua_md5}:{user_id}"
    USER_REFRESH_TOKEN = "user:refresh_token:{ua_md5}:{user_id}"

    EMAIL_ACTIVE = "user:email_active:{user_id}"
    EMAIL_ACTIVE_EXPIRED = 60 * 60 * 48
    EMAIL_ACTIVE_LIMIT = "user:email_active_limit:{user_id}"
    EMAIL_ACTIVE_LIMIT_EXPIRED = 60 * 60 * 24

    USER_CACHE = "user:cache:{user_id}"
    USER_CACHE_EXPIRED = 60 * 60 * 24

    INVENTORY_DEDUCT = "inventory:deduct:{id}"
    INVENTORY_DEDUCT_EXPIRED = 10
