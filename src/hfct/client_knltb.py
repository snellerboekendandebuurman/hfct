import json
import pytz
import requests

from datetime import datetime

from hfct.client_base import ClientBase

from .authentication_methods import AuthenticationMethods
from .exceptions import APIError


SIMPLE_KEY = "bGlzYXgtYXBpLXB1Yi11c2VyOjZUNmhyTTBOZTkxQlNqa3ZpSnhoOE1BalNucE4xTTl1"


class ClientKNLTB(ClientBase):
    BASE_URL = "https://api.knltb.club/"

    def __init__(self, x_lisa_auth_token=None, club_id=None, auth_method=None, kwargs=None):
        self.x_lisa_auth_token = x_lisa_auth_token
        self.club_id = club_id
        self.auth_method = auth_method
        self.kwargs = kwargs

        self.simple_key = SIMPLE_KEY

        self.session = requests.Session()

        if self.simple_key:
            self.session.headers.update({'Authorization': f'Basic {self.simple_key}'})

        if self.x_lisa_auth_token:
            self.session.headers.update({'x-lisa-auth-token': self.x_lisa_auth_token})

        self.session.headers.update({"Content-Type": "application/json"})

    def make_request(self, method, endpoint, data=None, retries=3):
        """
        Make a request to the API and handle unauthorized errors.
        This function will retry the request up to 'retries' times in case of a 401 response.
        """
        url = self._url_for(endpoint)
        response = self.session.request(method, url, data)

        if 200 <= response.status_code < 300:
            return response
        
        self.reauthenticate()
        return self.make_request(method, endpoint, data, retries=retries-1)

    def search_club(self, search_term):
        response = self.make_request("GET", f'v1/pub/tennis/federations/7E130D84-5644-4E38-9495-3B72A353E848/clubs?city_pattern={search_term}&page_number=1&name_pattern={search_term}&page_size=100')

        return self._handle_response(response, "Unable to search for club.")

    def authenticate_with_club_number_password(self, **kwargs) -> None:
        if not self.club_id:
            raise ValueError("Please provide club_id in order to login.")

        # Log the user in
        club_number = kwargs.get("club_number")
        password = kwargs.get("password")

        if not club_number or not password:
            raise ValueError("Both 'club_number' and 'password' must be provided.")

        payload = {
            "club_membership_number": club_number,
            "password": password
        }

        return self._login(payload)

    def authenticate_with_association_number_password(self, **kwargs) -> None:
        if not self.club_id:
            raise ValueError("Please provide club_id in order to login.")

        # Log the user in
        association_number = kwargs.get("association_number")
        password = kwargs.get("password")

        if not association_number or not password:
            raise ValueError("Both 'association_number' and 'password' must be provided.")

        payload = {
            "bond_number": association_number,
            "password": password
        }

        return self._login(payload)

    def reauthenticate(self):
        if self.auth_method == AuthenticationMethods.CLUB_NUMBER_PASSWORD:
            return self.authenticate_with_club_number_password(**self.kwargs)
        elif self.auth_method == AuthenticationMethods.ASSOCIATION_NUMBER_PASSWORD:
            return self.authenticate_with_association_number_password(**self.kwargs)
        else:
            raise ValueError(f"Unsupported authentication method: {self.auth_method}")

    def has_connection(self) -> bool:
        if not self.x_lisa_auth_token or not self.club_id:
            return False
        return True

    def search_player(self, search_name: str):
        if not self.has_connection():
            raise ValueError("Please login or provide 'club_id' & 'x_lisa_auth_token' to the Client")
        
        response = self.make_request("GET", f"v1/pub/tennis/clubs/{self.club_id}/members?page_size=25&name_pattern={search_name}&page_number=1")

        return self._handle_response(response, "Unable to search for player.")

    def book_court(self, sport_type, date, time_start, buddy_one_id, buddy_two_id, buddy_three_id, buddy_four_id):
        if not self.club_id or not self.x_lisa_auth_token:
            raise ValueError("Please login or provide 'club_id' & 'x_lisa_auth_token' to the Client")

        # TODO: Check if date is in: dd-mm-yyyy format

        # TODO: Check if time_start is in: hh:mm

        # Request URL when opening the "Spelen" page
        club_time_table_for_date = self.make_request("GET", f"v1/pub/tennis/clubs/{self.club_id}/availability_timeline?time_from={date}").json()

        timeline_court_availability = club_time_table_for_date.get("timeline_court_availability")

        formatted_date_time = self._format_date_time_from_cet_to_utc(date, time_start)

        court_details = self._get_first_available_court_id(timeline_court_availability, sport_type, formatted_date_time)

        if not court_details:
            raise APIError("No available court found")

        payload = {
            "reservation": {
                "start_at": formatted_date_time,
                "club_member_ids": [buddy_one_id, buddy_two_id, buddy_three_id, buddy_four_id],
                "products": [],
                "callback_url": "https://betalingen.knltb.club/AppCustomPages/redirectButton/tennis",
                "guests": [],
                "court_id": court_details.get("id")
	        }
        }

        # USE THIS RETURN FOR TESTING PURPOSES
        # return payload, court_details

        # BELOW IS THE CODE FOR MAKING THE BOOKING FINAL
        # FOR NOW WE WILL ONLY RETURN THE PAYLOAD
        response = self.make_request("POST", f"/v1/pub/tennis/clubs/{self.club_id}/reservations", data=json.dumps(payload))
        return self._handle_response(response, "Unable to search for club."), court_details


    def _url_for(self, endpoint):
        return f"{self.BASE_URL}{endpoint}"

    def _handle_response(self, response, error_message):
        # This assumes a JSON API. Adjust as necessary for other response types.

        if 200 <= response.status_code < 300:
            return response.json()
        # Use custom error_message, since there was no available one in the response
        raise APIError(error_message)

    def _login(self, payload):
        # The login will only be tried once, no need to use the self.make_request method.
        response = self.session.post(self._url_for(f"v1/pub/tennis/clubs/{self.club_id}/auth_tokens"), data=json.dumps(payload))

        parsed_response = self._handle_response(response, "Unable to login.")

        x_lisa_auth_token = parsed_response.get("token")
        if x_lisa_auth_token:
            self.x_lisa_auth_token = x_lisa_auth_token
            self.session.headers.update({'x-lisa-auth-token': self.x_lisa_auth_token})

        return parsed_response

    def _get_first_available_court_id(self, timeline_court_availability, sport_type, start_date_time):
        for _, court_information in enumerate(timeline_court_availability):
            court_details = court_information.get("court_details")
            sport = court_details.get("sport").lower()
            if sport != sport_type.lower():
                continue

            court_timeline = court_information.get("timeline")
            blocks = court_timeline.get("blocks")
            for block in blocks:
                available = block.get("block_type").lower()

                if available != "available":
                    continue

                slots = block.get("slots")
                slots_list = []

                slots_list.extend(slots.get("2players"))
                slots_list.extend(slots.get("3players"))
                slots_list.extend(slots.get("4players"))

                for slot in slots_list:
                    start_time = slot.get("start_time")

                    if start_time != start_date_time:
                        continue

                    return court_details

    def _format_date_time_from_cet_to_utc(self, date, time):
        datetime_str = date + " " + time
        cet = pytz.timezone('CET')

        # Convert the combined string to a datetime object in CET timezone
        local_dt = cet.localize(datetime.strptime(datetime_str, '%Y-%m-%d %H:%M'))

        # Convert the datetime to UTC
        utc_dt = local_dt.astimezone(pytz.utc)

        # Format the datetime in the desired format
        return utc_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
