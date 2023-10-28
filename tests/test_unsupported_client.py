import pytest

from hfct.client import AuthenticationMethods, authenticate


class TestClientUnsupported:
    def test_unsupported_broker(self) -> None:
        client = "non_existing_client"
        with pytest.raises(ValueError) as exc_info:
            authenticate(client, AuthenticationMethods.CLUB_NUMBER_PASSWORD)

        assert str(exc_info.value) == f"Unsupported client: {client}"
