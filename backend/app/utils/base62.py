# divmod(value, 62) returns the next quotient and one alphabet index.
# The remainder ranges from zero through len(ALPHABET) - 1.
# divmod(125, 62) returns (2, 1). Each iteration keeps the quotient.
# ALPHABET[1] is "1". ALPHABET[36] is "A".
# Reversing the collected digits restores most-significant-digit order.

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def encode_base62(value: int)-> str:
    if value < 0:
        raise ValueError ("Base62 cannot encode negative values")

    if value==0:
        return ALPHABET[0]
    characters: list[str]=[]
    while value>0:
        value, remainder=divmod(value,len(ALPHABET))
        characters.append(ALPHABET[remainder])

    return "".join(reversed(characters))
