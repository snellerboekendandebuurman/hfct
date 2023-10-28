from .client_base import ClientBase
from .client_knltb import ClientKNLTB
from .clients import Clients


class ClientFactory:
    @staticmethod
    def create_client(client_name: Clients, **kwargs) -> ClientBase:
        if client_name == Clients.KNLTB:
            x_lisa_auth_token = kwargs.get("x_lisa_auth_token")
            club_id = kwargs.get("club_id")

            return ClientKNLTB(x_lisa_auth_token=x_lisa_auth_token, club_id=club_id)
        else:
            raise ValueError(f"Unsupported client: {client_name}")
