import json
import pytz
import requests

from datetime import datetime

from hfct.client_base import ClientBase


from .exceptions import APIError


SIMPLE_KEY = "bGlzYXgtYXBpLXB1Yi11c2VyOjZUNmhyTTBOZTkxQlNqa3ZpSnhoOE1BalNucE4xTTl1"


class ClientKNLTB(ClientBase):
    BASE_URL = "https://api.knltb.club/"

    def __init__(self, x_lisa_auth_token=None, club_id=None):
        self.x_lisa_auth_token = x_lisa_auth_token
        self.club_id = club_id

        self.simple_key = SIMPLE_KEY

        self.session = requests.Session()

        if self.simple_key:
            self.session.headers.update({'Authorization': f'Basic {self.simple_key}'})

        if self.x_lisa_auth_token:
            self.session.headers.update({'x-lisa-auth-token': self.x_lisa_auth_token})

        self.session.headers.update({"Content-Type": "application/json"})

    def search_club(self, search_term):
        response = self.session.get(self._url_for(f'v1/pub/tennis/federations/7E130D84-5644-4E38-9495-3B72A353E848/clubs?city_pattern={search_term}&page_number=1&name_pattern={search_term}&page_size=100'))
        return self._handle_response(response)

    def authenticate_with_club_number_password(self, **kwargs) -> None:
        club_id = kwargs.get("club_id")
        club_number = kwargs.get("club_number")
        password = kwargs.get("password")

        if not club_number or not password or not club_id:
            raise ValueError("Both 'club_number', 'password' and 'club_id' must be provided.")

        payload = {
            "club_number": club_number,
            "password": password
        }

        return self._login(club_id, payload)

    def authenticate_with_association_number_password(self, **kwargs) -> None:
        club_id = kwargs.get("club_id")
        association_number = kwargs.get("association_number")
        password = kwargs.get("password")

        if not association_number or not password or not club_id:
            raise ValueError("Both 'club_number', 'password' and 'club_id' must be provided.")

        payload = {
            "bond_number": association_number,
            "password": password
        }

        return self._login(club_id, payload)

    def has_connection(self) -> bool:
        if not self.x_lisa_auth_token or not self.club_id:
            return False

        # TODO: Check if the current x_lisa_auth_token is still valid
        #       if that's not the case, refresh is if possible.

        return True



    def seach_player(self, search_name):
        if not self.club_id or not self.x_lisa_auth_token:
            raise ValueError("Please login or provide 'club_id' & 'x_lisa_auth_token' to the Client")

        response = self.session.get(self._url_for(f"v1/pub/tennis/clubs/{club_id}/members?page_size=25&name_pattern={search_name}&page_number=1"))

        return self._handle_response(response)

    def book_court(self, sport_type, date, time_start, buddy_one_id, buddy_two_id, buddy_three_id, buddy_four_id):
        if not self.club_id or not self.x_lisa_auth_token:
            raise ValueError("Please login or provide 'club_id' & 'x_lisa_auth_token' to the Client")

        # Check if date is in: dd-mm-yyyy format

        # Check if time_start is in: hh:mm

        # Request URL when opening the "Spelen" page
        club_time_table_for_date = self.session.get(self._url_for(f"v1/pub/tennis/clubs/{self.club_id}/availability_timeline?time_from={date}")).json()

        timeline_court_availability = club_time_table_for_date.get("timeline_court_availability")

        formatted_date_time = self._format_date_time_from_cet_to_utc(date, time_start)

        court_id = self._get_first_available_court_id(timeline_court_availability, sport_type, formatted_date_time)

        payload = {
            "reservation": {
                "start_at": formatted_date_time,
                "club_member_ids": [buddy_one_id, buddy_two_id, buddy_three_id, buddy_four_id],
                "products": [],
                "callback_url": "https:\/\/betalingen.knltb.club\/AppCustomPages\/redirectButton\/tennis",
                "guests": [],
                "court_id": court_id
	        }
        }

        return payload
        # BELOW IS THE CODE FOR MAKING THE BOOKING FINAL
        # FOR NOW WE WILL ONLY RETURN THE PAYLOAD

        # response = self.session.post(self._url_for(f"/v1/pub/tennis/clubs/{club_id}/reservations"), data=json.dumps(payload))

        # return self._handle_response(response)

    def _url_for(self, endpoint):
        return f"{self.BASE_URL}{endpoint}"

    def _handle_response(self, response):
        # This assumes a JSON API. Adjust as necessary for other response types.
        data = response.json()

        if 200 <= response.status_code < 300:
            return data
        raise APIError(data.get('error', 'Unknown error'))

    def _login(self, club_id, payload):
        self.club_id = club_id

        response = self.session.post(self._url_for(f"v1/pub/tennis/clubs/{self.club_id}/auth_tokens"), data=json.dumps(payload)).json()

        # TODO: Check for an OK response

        x_lisa_auth_token = response.get("token")
        if x_lisa_auth_token:
            self.x_lisa_auth_token = x_lisa_auth_token
            self.session.headers.update({'x-lisa-auth-token': self.x_lisa_auth_token})

        return response

    def _get_first_available_court_id(self, timeline_court_availability, sport_type, start_date_time):
        for i, court_information in enumerate(timeline_court_availability):
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

                    return court_details.get("id")

    def _format_date_time_from_cet_to_utc(self, date, time):
        datetime_str = date + " " + time
        cet = pytz.timezone('CET')

        # Convert the combined string to a datetime object in CET timezone
        local_dt = cet.localize(datetime.strptime(datetime_str, '%Y-%m-%d %H:%M'))

        # Convert the datetime to UTC
        utc_dt = local_dt.astimezone(pytz.utc)

        # Format the datetime in the desired format
        return utc_dt.strftime('%Y-%m-%dT%H:%M:%SZ')


# client = APIClient("")

# Search for Club Info
# response = client.search_club("HC Tilburg")


# LOGIN TCT
# response = client.club_login("3e4e3dee-888f-4471-ac0e-08474b5e572c", "club_number", "12620", "LG7E3aZcPBoiYU47F6@$")


# LOGIN HC TILBURG
# response = client.club_login("0009fb2d-b99b-4e18-9923-61a02b3c7a68", "club_number", "160", "Lu82Fc^Mr@TVY4t@PtKq")

# Book court
# response = client.club_book_court("0009fb2d-b99b-4e18-9923-61a02b3c7a68", "padel", "2023-10-20", "18:30", "8e41743f-9940-4f66-a44d-d40f80196471", "48cff314-c99b-44f1-bf5b-a660b1f03f55", "7edf7eb7-2e67-403b-9f34-352d3e0929b5", "d3d53db0-144c-4a63-b1d3-a3a0bb9f7e5f")

# import pdb; pdb.set_trace()

# def club_login(self, club_id, login_method, number, password):
#     method = "club_membership_number" if login_method == "club_number" else "bond_number"
#
#     payload = {
#         method: number,
#         "password": password
#     }
#
#     response = self.session.post(self._url_for(f"v1/pub/tennis/clubs/{club_id}/auth_tokens"), data=json.dumps(payload)).json()
#
#     x_lisa_auth_token = response.get("token")
#     if x_lisa_auth_token:
#         self.x_lisa_auth_token = x_lisa_auth_token
#         self.session.headers.update({'x-lisa-auth-token': self.x_lisa_auth_token})
#
#     return response
