import random
import string


class Random:
    @staticmethod
    def generate_number(length):
        return "".join(random.sample(string.digits, length))

    @staticmethod
    def generate(length):
        return "".join(random.sample(f"{string.digits}{string.ascii_letters}{string.punctuation}", length))
