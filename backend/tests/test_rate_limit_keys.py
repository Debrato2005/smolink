from app.api.v1.dependencies.rate_limit import client_rate_key


def test_ipv4_and_missing_clients_keep_their_identity() -> None:
    assert client_rate_key("203.0.113.7") == "203.0.113.7"
    assert client_rate_key(None) == "unknown"
    assert client_rate_key("") == "unknown"
    assert client_rate_key("testclient") == "testclient"


def test_ipv6_addresses_in_one_slash_64_share_a_key() -> None:
    first = client_rate_key("2001:db8:1:2:aaaa:bbbb:cccc:dddd")
    second = client_rate_key("2001:db8:1:2::1")
    assert first == second == "2001:db8:1:2::/64"
    assert client_rate_key("2001:db8:1:3::1") != first


def test_ipv4_mapped_ipv6_is_keyed_as_ipv4() -> None:
    assert client_rate_key("::ffff:203.0.113.7") == "203.0.113.7"
