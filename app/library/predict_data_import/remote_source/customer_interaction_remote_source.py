from abc import ABC, abstractmethod


class CustomerInteractionRemoteSource(ABC):
    """
    This class is the interface that declare the methods required to interact with the remote repository
    """
    @abstractmethod
    def download_customer_interaction_csv(self, local_file_path: str, number_of_week: int) -> None:
        """Download customer interaction locally into CSV file"""
        pass
