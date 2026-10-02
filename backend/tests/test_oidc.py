# The challenge vector comes from RFC 7636 Appendix B.
# Target PKCE exchange: send challenge at authorization, then code and verifier.
# Helpers and Google routes remain unfinished in the current working tree.

import re 

from app.utils.oidc import (
    create_pkce_challenge,
    create_pkce_verifier,
)

def test_pkce_challenge_matches_rfc_7636_vector() -> None:
    verifier = (
        "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_"
        "wW1gFWFOEjXk"
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
