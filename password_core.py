"""COS738 deterministic password derivation, version 1.

AI-assisted re-engineering of the supplied educational example. All constants,
UTF-8 encoding and byte order are mirrored in password_core.js. Changing any
algorithm constant changes previously generated passwords. Educational use only:
a public fixed salt does not protect a guessable memorable input from guessing.
"""
import hashlib
import string

UPPER = string.ascii_uppercase
LOWER = string.ascii_lowercase
DIGITS = string.digits
SYMBOLS = "!@#$%^&*()-_=+[]{};:,.<>/?"
CATEGORIES = (UPPER, LOWER, DIGITS, SYMBOLS)
CHARSET = "".join(CATEGORIES)
SALT = b"COS738-PasswordGenerator-v1"
ITERATIONS = 200_000
MIN_LENGTH, MAX_LENGTH = 8, 128
MAX_INPUT_BYTES = 1024


def validate_inputs(memorable: str, length: int) -> None:
    """Reject invalid inputs without stripping or normalising valid text."""
    if not isinstance(memorable, str) or not memorable.strip():
        raise ValueError("Enter a memorable password, not just spaces.")
    if len(memorable.encode("utf-8")) > MAX_INPUT_BYTES:
        raise ValueError("Memorable password must be at most 1024 UTF-8 bytes.")
    if type(length) is not int or not MIN_LENGTH <= length <= MAX_LENGTH:
        raise ValueError("Output length must be a whole number from 8 to 128.")


class ByteStream:
    """Deterministic SHA-256 expansion with a four-byte big-endian counter."""
    def __init__(self, seed: bytes):
        self.seed, self.counter, self.buffer = seed, 0, bytearray()

    def choose(self, size: int) -> int:
        """Rejection sampling avoids modulo bias for ranges up to 256."""
        limit = 256 - 256 % size
        while True:
            if not self.buffer:
                self.buffer.extend(hashlib.sha256(
                    self.seed + self.counter.to_bytes(4, "big")).digest())
                self.counter += 1
            value = self.buffer.pop(0)
            if value < limit:
                return value % size


def derive_password(memorable: str, length: int = 24) -> str:
    """Return exactly length characters, including all four character classes.

    The length is part of the salt. Inputs are case/space-sensitive; no Unicode
    normalisation is performed. This is derivation, not reversible encryption.
    """
    validate_inputs(memorable, length)
    salt = SALT + b":" + str(length).encode("ascii")
    seed = hashlib.pbkdf2_hmac("sha256", memorable.encode("utf-8"), salt,
                               ITERATIONS, dklen=32)
    stream = ByteStream(seed)
    # Reserve one character per class, avoiding the example's repair overwrite bug.
    result = [category[stream.choose(len(category))] for category in CATEGORIES]
    result.extend(CHARSET[stream.choose(len(CHARSET))] for _ in range(length - 4))
    # Shuffle so mandatory categories do not occupy fixed positions.
    for index in range(length - 1, 0, -1):
        other = stream.choose(index + 1)
        result[index], result[other] = result[other], result[index]
    return "".join(result)
