"""Tests for the Argon2id password primitives."""

from src.security.passwords import (
    hash_password,
    password_needs_rehash,
    verify_password,
)


def test_hash_password_uses_argon2id_with_random_salts() -> None:
    password = "frase secreta pedagógica"

    first_hash = hash_password(password)
    second_hash = hash_password(password)

    assert first_hash.startswith("$argon2id$")
    assert second_hash.startswith("$argon2id$")
    assert first_hash != second_hash
    assert verify_password(first_hash, password)
    assert verify_password(second_hash, password)


def test_verify_password_rejects_mismatch_and_malformed_hash() -> None:
    password_hash = hash_password("frase secreta pedagógica")

    assert not verify_password(password_hash, "outra frase secreta")
    assert not verify_password("hash-inválido", "frase secreta pedagógica")


def test_current_hash_does_not_need_rehash() -> None:
    password_hash = hash_password("frase secreta pedagógica")

    assert password_needs_rehash(password_hash) is False
    assert password_needs_rehash("hash-inválido") is True
