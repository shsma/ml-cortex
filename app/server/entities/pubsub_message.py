import json


class Metadata:
    def __init__(self, publication_timestamp: int, topic_name: str):
        self.publication_timestamp = publication_timestamp
        self.topic_name = topic_name


class Aggregate:
    def __init__(self, id: str, state: str, business_entity: str,
                 aggregate_version: int, type: str, version: str,
                 gender: int, location: str, url: str):
        self.id = id
        self.state = state
        self.business_entity = business_entity
        self.aggregate_version = aggregate_version
        self.type = type
        self.version = version
        self.gender = gender
        self.location = location
        self.url = url


class PubsubMessage:
    TOPIC_NAME = 'MachineLearning.Model'
    BUSINESS_ENTITY = 'Model'
    TYPE = 'brand_gender'

    def __init__(self, metadata: Metadata, aggregate: Aggregate):
        self.metadata = metadata
        self.aggregate = aggregate

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def __repr__(self):
        return self.to_json()
