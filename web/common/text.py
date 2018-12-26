import random
import string


def obfuscate(text):
    chars = []
    for c in text:
        if c == ' ':
            new_c = ' '
        else:
            new_c = random.choice(string.ascii_letters)

        if c.isupper():
            new_c.upper()

        chars.append(new_c)

    return ''.join(chars)
