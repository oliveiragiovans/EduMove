"""Argon2id password hashing and verification."""

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from argon2.low_level import Type


# OWASP minimum Argon2id profile: 19 MiB, two iterations, one lane.
_PASSWORD_HASHER = PasswordHasher(
    time_cost=2,
    memory_cost=19 * 1024,
    parallelism=1,
    hash_len=32,
    salt_len=16,
    type=Type.ID,
)


def hash_password(password: str) -> str:
    """Create a salted Argon2id hash for a validated password."""

    return _PASSWORD_HASHER.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    """Safely return whether a password matches an encoded hash."""

    try:
        return _PASSWORD_HASHER.verify(password_hash, password)
    except (VerificationError, ValueError, TypeError):
        return False


def password_needs_rehash(password_hash: str) -> bool:
    """Return whether a valid hash should be upgraded after login."""

    try:
        return _PASSWORD_HASHER.check_needs_rehash(password_hash)
    except (ValueError, TypeError):
        return True
