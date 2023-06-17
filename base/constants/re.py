class ReConstants:
    USERNAME_PATTERN = r"[0-9a-zA-Z_-]{5,16}"
    MOBILE_PATTERN = r"^1(3|4|5|6|7|8|9)\d{9}$"
    PASSWORD_PATTERN = r"^(?![0-9]+$)(?![a-z]+$)(?![A-Z]+$)(?![\~`!@#\$%\^&\*\(\)\-_\+\=\[\]\{\}\\\|;:\'\",\<\.\>\?\/]+$)[\~`!@#\$%\^&\*\(\)\-_\+\=\[\]\{\}\\\|;:\'\",\<\.\>\?\/0-9A-Za-z]{8,16}$"  # noqa
