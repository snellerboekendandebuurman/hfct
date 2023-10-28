from abc import ABC, abstractmethod


class ClientBase(ABC):
    @abstractmethod
    def has_connection(self) -> bool:
        pass

    @abstractmethod
    def authenticate_with_club_number_password(self, **kwargs) -> None:
        pass

    @abstractmethod
    def authenticate_with_association_number_password(self, **kwargs) -> None:
        pass

    @abstractmethod
    def search_player(self, search_name: str) -> None:
        pass

    @abstractmethod
    def book_court(self, sport_type: str, date: str, time_start: str, buddy_one_id: str, buddy_two_id: str, buddy_three_id: str, buddy_four_id: str) -> None:
        pass
    # @abstractmethod
    # def logout(self, **kwargs) -> None:
    #     pass

