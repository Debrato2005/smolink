from app.utils.security import hash_password, verify_password

from app.utils.security import hash_password, normalize_email, verify_password

def test_password_hash_is_argon2id_and_verifiable()->None:
    password="hello1345678"
    password_hash=hash_password(password)

    assert password_hash!=password
    assert password_hash.startswith("$argon2id$")
    assert verify_password(password,password_hash)
    assert not verify_password("wrong12345678",password_hash)

def test_normalize_email_strips_and_lowercases() -> None:
    assert normalize_email(" User.Name@Example.COM ") == "user.name@example.com"

# Passwords are never stored or compared in plaintext. Instead, they are
# hashed using Argon2id, a password hashing algorithm designed to be slow and
# memory-hard, making brute-force attacks computationally expensive.
#
# Each password is hashed with a cryptographically secure random salt, ensuring
# that identical passwords produce different hashes. The generated hash embeds
# the algorithm, hashing parameters, salt, and final hash in a single string,
# allowing password verification without storing the original password or a
# separate salt column.
#
# During login, the stored hash is parsed to recover the original hashing
# parameters and salt. Argon2 hashes the user-provided password again using
# those same values, and authentication succeeds only if the newly computed
# hash matches the stored hash.
#
# These tests verify that passwords are hashed with Argon2id, never stored in
# plaintext, and that password verification succeeds only for the correct
# password while rejecting incorrect ones.