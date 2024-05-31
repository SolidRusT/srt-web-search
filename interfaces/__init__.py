import abc


class UIProvider(abc.ABC):

    @abc.abstractmethod
    def setup_ui(self):
        """
        Method that sets up the UI provider.
        """
        pass

    @abc.abstractmethod
    def start_ui_provider(self, **kwargs):
        """
        Method that starts up the UI provider.
        """
        pass
