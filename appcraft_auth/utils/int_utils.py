import random
import string


def generate_random_digits(length):
    return ''.join(random.sample(string.digits, length))
