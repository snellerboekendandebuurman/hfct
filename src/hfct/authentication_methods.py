from .utils import BaseEnum


class AuthenticationMethods(BaseEnum):
    CLUB_NUMBER_PASSWORD = "club number and password"
    ASSOCIATION_NUMBER_PASSWORD = "association number and password"