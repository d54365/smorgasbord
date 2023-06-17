import pickle


class CacheSerializer:
    def __init__(self, protocol=None):
        self.protocol = pickle.HIGHEST_PROTOCOL if protocol is None else protocol

    def dumps(self, obj):
        if type(obj) is int:
            return obj
        return pickle.dumps(obj, self.protocol)

    @staticmethod
    def loads(data):
        try:
            return int(data)
        except ValueError:
            return pickle.loads(data)
