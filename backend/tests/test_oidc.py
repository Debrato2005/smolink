import re 

from app.utils.oidc import (
    create_pkce_challenge,
    create_pkce_verifier,
)

def test_pkce_challenge_matches_rfc_7636_vector() -> None:
    verifier = (
        "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_"
        "wW1gFWFOEjXk" #This uses a known official PKCE example.
    )

    assert create_pkce_challenge(verifier) == (
        "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM"
    )


def test_pkce_verifier_is_valid_and_unique() -> None:
    first = create_pkce_verifier()
    second = create_pkce_verifier()

    assert 43 <= len(first) <= 128
    assert re.fullmatch(r"[A-Za-z0-9._~-]+", first)
    assert first != second   

# 1. Smolink sends CHALLENGE to Google
# 2. Google gives AUTHORIZATION CODE to Smolink
# 3. Smolink sends CODE + VERIFIER to Google
# 4. Google gives TOKENS to Smolink