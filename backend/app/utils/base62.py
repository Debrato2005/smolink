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

# divmod(a, b) returns a tuple: (quotient, remainder)
#
# Example:
#     divmod(125, 62) -> (2, 1)
#
# Tuple unpacking assigns:
#     value, remainder = divmod(value, len(ALPHABET))
#
# which is equivalent to:
#     result = divmod(value, len(ALPHABET))
#     value = result[0]      # quotient
#     remainder = result[1]  # remainder
#
# The quotient becomes the new value for the next iteration.
# The remainder is always in the range [0, len(ALPHABET)-1], making it
# a valid index into ALPHABET.
#
# Example:
#     remainder = 1
#     ALPHABET[1] -> "1"
#
#     remainder = 36
#     ALPHABET[36] -> "A"
#
# Thus, each remainder directly selects the corresponding Base62 digit.