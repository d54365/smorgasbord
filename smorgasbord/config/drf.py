REST_FRAMEWORK = {
    "SEARCH_PARAM": "search",
    "ORDERING_PARAM": "ordering",
    "EXCEPTION_HANDLER": "base.exceptions.exception_handler.exception_handler",
    # 格式化时间
    "DATETIME_FORMAT": "%Y-%m-%d %H:%M:%S",
    "DATETIME_INPUT_FORMATS": ("%Y-%m-%d %H:%M:%S",),
    "DATE_FORMAT": "%Y-%m-%d",
    "TIME_FORMAT": "%H:%M",
    "DEFAULT_RENDERER_CLASSES": (
        "base.utils.renderers.ORJSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ),
}
