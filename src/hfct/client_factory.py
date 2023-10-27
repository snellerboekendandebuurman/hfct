from .client_base import ClientBase
from .client_knltb import ClientKNLTB
from .clients import Clients


class ClientFactory:
    @staticmethod
    def create_client(client_name: Clients) -> ClientBase:
        if client_name == Clients.KNLTB:
            return ClientKNLTB()
        else:
            raise ValueError(f"Unsupported client: {client_name}")
