class SMSSender:
    def __init__(self, access_key, secret, domain, region):
        self._access_key = access_key
        self._secret = secret
        self._region = region
        self._domain = domain

    def send(self, sign_name, mobile, template, params):
        raise NotImplementedError
