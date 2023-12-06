from .authentication_methods import AuthenticationMethods
from .client_base import ClientBase
from .client_factory import ClientFactory
from .clients import Clients


def authenticate(client_name: Clients, auth_method: AuthenticationMethods, **kwargs) -> ClientBase:
    client = ClientFactory.create_client(client_name, auth_method, **kwargs)

    if client.has_connection():
        return client

    if auth_method == AuthenticationMethods.CLUB_NUMBER_PASSWORD:
        client.authenticate_with_club_number_password(**kwargs)
    elif auth_method == AuthenticationMethods.ASSOCIATION_NUMBER_PASSWORD:
        client.authenticate_with_association_number_password(**kwargs)
    else:
        raise ValueError(f"Unsupported authentication method: {auth_method}")

    return client


# def logout(broker_connection: BrokerBase, auth_method: AuthenticationMethods, **kwargs) -> None:
#     if auth_method == AuthenticationMethods.USERNAME_PASSWORD:
#         broker_connection.logout_with_username_password(**kwargs)
#     else:
#         raise ValueError(f"Unsupported logout method: {auth_method}")
