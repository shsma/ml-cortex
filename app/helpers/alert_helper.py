import logging
import slack

from app.db_update_app.config import Config


class AlertHelper:
    # Store the instance in this variable
    instance = None

    @staticmethod
    def get_instance():
        # Static access method
        if AlertHelper.instance is None:
            raise RuntimeError('Alert Helper not instantiated')

        return AlertHelper.instance

    def __init__(self, config: Config):
        """ Virtually private constructor. """
        if AlertHelper.instance is None:
            # set std_out
            self.user_name = f'{config.APP_NAME}-{config.ENV}'
            self.client = slack.WebClient(token=config.SLACK_TOKEN)
            self.channel = config.SLACK_CHANNEL
            self.logging_level = config.LOGGING_LEVEL
            self.enabled = config.SLACK_ENABLED
            AlertHelper.instance = self

    def __post(self, level: int, message: str):
        if self.enabled is not True:
            return

        if level < self.logging_level:
            return

        self.client.chat_postMessage(
            username=self.user_name,
            channel=self.channel,
            text=f'[{logging.getLevelName(level)}] {message}'
        )

    def error(self, message: str):
        self.__post(level=logging.ERROR, message=message)

    def debug(self, message: str):
        self.__post(level=logging.DEBUG, message=message)

    def info(self, message: str):
        self.__post(level=logging.INFO, message=message)
