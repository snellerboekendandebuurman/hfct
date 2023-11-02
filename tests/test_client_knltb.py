import pytest
from hfct import client_knltb
from hfct.client import AuthenticationMethods, authenticate

from hfct.client_knltb import ClientKNLTB
from hfct.clients import Clients
from hfct.exceptions import APIError


CLUB_ID_HCTILBURG = "0009fb2d-b99b-4e18-9923-61a02b3c7a68"
CLUB_NUMBER_JORIS_JANSEN = 160
CLUB_PASSWORD_JORIS_JANSEN = "Lu82Fc^Mr@TVY4t@PtKq"


class TestClientKNLTBSearchClub:
    def test_search_unknown_club(self) -> None:
        client = ClientKNLTB()
        result = client.search_club("FooBar")

        assert "clubs" in result
        assert "page" in result
        assert "page_number" in result["page"]
        assert "page_size" in result["page"]
        assert "total_entries" in result["page"]
        assert "total_pages" in result["page"]
        assert result["page"]["page_number"] == 1
        assert result["page"]["page_size"] == 100
        assert result["page"]["total_entries"] == 0
        assert result["page"]["total_pages"] == 0

    def test_search_hc_tilburg(self) -> None:
        client = ClientKNLTB()
        result = client.search_club("hc tilburg")

        assert "clubs" in result
        assert "page" in result
        assert "page_number" in result["page"]
        assert "page_size" in result["page"]
        assert "total_entries" in result["page"]
        assert "total_pages" in result["page"]
        assert result["page"]["page_number"] == 1
        assert result["page"]["page_size"] == 100
        assert result["page"]["total_entries"] == 1
        assert result["page"]["total_pages"] == 1

        assert len(result["clubs"]) == 1
        assert "club" in result["clubs"][0]
        assert "logo_url" in result["clubs"][0]["club"]
        assert "locale" in result["clubs"][0]["club"]
        assert "id" in result["clubs"][0]["club"]
        assert "city" in result["clubs"][0]["club"]
        assert "federation_code" in result["clubs"][0]["club"]
        assert "short_name" in result["clubs"][0]["club"]
        assert "is_hockey" in result["clubs"][0]["club"]
        assert "favicon_url" in result["clubs"][0]["club"]
        assert "my_env_login_background" in result["clubs"][0]["club"]
        assert "branded_clubapp_ios_store_link" in result["clubs"][0]["club"]
        assert "branded_clubapp_android_store_link" in result["clubs"][0]["club"]
        assert "has_branded_app" in result["clubs"][0]["club"]
        assert "name" in result["clubs"][0]["club"]

    def test_authenticate_club_number_password_without_club_id(self) -> None:
        with pytest.raises(ValueError) as exc_info:
            authenticate(Clients.KNLTB, AuthenticationMethods.CLUB_NUMBER_PASSWORD)

        assert str(exc_info.value) == "Please provide club_id in order to login."

    def test_authenticate_club_number_password_without_club_number(self) -> None:
        with pytest.raises(ValueError) as exc_info:
            authenticate(Clients.KNLTB, AuthenticationMethods.CLUB_NUMBER_PASSWORD, club_id="123abc")

        assert str(exc_info.value) == "Both 'club_number' and 'password' must be provided."

    def test_authenticate_club_number_password_without_password(self) -> None:
        with pytest.raises(ValueError) as exc_info:
            authenticate(Clients.KNLTB, AuthenticationMethods.CLUB_NUMBER_PASSWORD, club_id="123abc", club_number="abc321")

        assert str(exc_info.value) == "Both 'club_number' and 'password' must be provided."


    def test_authenticate_club_number_password_unsuccessful(self) -> None:
        with pytest.raises(APIError) as error:
            authenticate(Clients.KNLTB, AuthenticationMethods.CLUB_NUMBER_PASSWORD, club_id=CLUB_ID_HCTILBURG, club_number=CLUB_NUMBER_JORIS_JANSEN, password="test123123")

        assert str(error.value) == "Unable to login."

    def test_authenticate_club_number_password_successful(self) -> None:
        client_knltb = authenticate(Clients.KNLTB, AuthenticationMethods.CLUB_NUMBER_PASSWORD, club_id=CLUB_ID_HCTILBURG, club_number=CLUB_NUMBER_JORIS_JANSEN, password=CLUB_PASSWORD_JORIS_JANSEN)

        assert client_knltb.club_id is not None
        assert client_knltb.x_lisa_auth_token is not None
        assert client_knltb.simple_key is not None
        assert client_knltb.has_connection() == True

    def test_authenticate_with_x_lisa_auth_token_and_club_id(self) -> None:
        client_knltb = authenticate(Clients.KNLTB, AuthenticationMethods.CLUB_NUMBER_PASSWORD, club_id=CLUB_ID_HCTILBURG, club_number=CLUB_NUMBER_JORIS_JANSEN, password=CLUB_PASSWORD_JORIS_JANSEN)

        x_lisa_auth_token = client_knltb.x_lisa_auth_token

        client_knltb_new = authenticate(client_name=Clients.KNLTB, auth_method=AuthenticationMethods.CLUB_NUMBER_PASSWORD, club_id=CLUB_ID_HCTILBURG, x_lisa_auth_token=x_lisa_auth_token)

        assert client_knltb_new.club_id is not None
        assert client_knltb_new.x_lisa_auth_token is not None
        assert client_knltb_new.simple_key is not None
        assert client_knltb_new.has_connection() == True

    def test_search_player_unsuccessful(self) -> None:
        with pytest.raises(APIError) as error:
            client_knltb = authenticate(client_name=Clients.KNLTB, auth_method=AuthenticationMethods.CLUB_NUMBER_PASSWORD, club_id=CLUB_ID_HCTILBURG, x_lisa_auth_token="30237njsdfh=")
            client_knltb.search_player("Joris Jansen")

            assert str(error.value) == "Unable to search player."

    def test_search_player_successful(self) -> None:
        client_knltb = authenticate(Clients.KNLTB, AuthenticationMethods.CLUB_NUMBER_PASSWORD, club_id=CLUB_ID_HCTILBURG, club_number=CLUB_NUMBER_JORIS_JANSEN, password=CLUB_PASSWORD_JORIS_JANSEN)

        assert client_knltb.club_id is not None
        assert client_knltb.x_lisa_auth_token is not None
        assert client_knltb.simple_key is not None
        assert client_knltb.has_connection() == True

        response = client_knltb.search_player("Joris Jansen")

        assert "club_members" in response
        assert "page" in response
        assert len(response["club_members"]) == 1
        assert response["page"]["page_number"] == 1
        assert response["page"]["page_size"] == 25
        assert response["page"]["total_entries"] == 1
        assert response["page"]["total_pages"] == 1
