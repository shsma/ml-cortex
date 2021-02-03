import json

import requests

from app.config import Config
from app.server.entities.pubsub_message import PubsubMessage


def _generate_error_message(attribute: str, property: str) -> str:
    return f'Missing {attribute} property from {property}'


class PubSubService:

    def __init__(self, config: Config):
        self.host = config["PUBSUB_HOST"]
        self.port = config["PUBSUB_PORT"]
        self.publisher = config["PUBSUB_PUBLISHER"]
        self.protocol = config["PUBSUB_PROTOCOL"]

    def send_message(self, pubsub_message: PubsubMessage):
        """
        Send a pubsub message
        :param pubsub_message:
        :return:
        """

        if not pubsub_message.metadata.topic_name:
            raise Exception(_generate_error_message('topic_name', 'metadata'))

        if not pubsub_message.metadata.publication_timestamp:
            raise Exception(_generate_error_message('publication_timestamp', 'metadata'))

        if not pubsub_message.aggregate.id:
            raise Exception(_generate_error_message('id', 'aggregate'))

        if not pubsub_message.aggregate.state:
            raise Exception(_generate_error_message('state', 'aggregate'))

        if not pubsub_message.aggregate.business_entity:
            raise Exception(_generate_error_message('business_entity', 'aggregate'))

        if not pubsub_message.aggregate.aggregate_version:
            raise Exception(_generate_error_message('aggregate_version', 'aggregate'))

        return requests.post(
            url=f'{self.protocol}://{self.host}/messages',
            headers={
                'Content-Type': 'application/json',
            },
            json=json.loads(pubsub_message.to_json())
        )
