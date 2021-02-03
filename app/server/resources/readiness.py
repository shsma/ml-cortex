import time
import uuid
import traceback
from flask import make_response
from flask_restful import Resource
from werkzeug import Response

from ssense_logger.app_logger import AppLogger
from app.server.entities.pubsub_message import Aggregate, PubsubMessage, Metadata
from app.server.services.pubsub import PubSubService


class Readiness(Resource):

    def __init__(self, **kwargs):
        self.config = kwargs['config']
        self.pubsub_service = PubSubService(self.config)
        self.app_logger = kwargs['app_logger']

    def get(self) -> Response:
        self.app_logger.debug(msg=f"PUBSUB_EVENT_SENT: {self.config['PUBSUB_EVENT_SENT']}")

        if self.config['PUBSUB_EVENT_SENT']:
            self.app_logger.debug(msg='pubsub already sent. skipping')
            return make_response({'status': 'ok', self.config.get('APP_NAME'): 'ready', 'response_code': 200})

        # model is considered ready, emit the event if it hasn't already been
        self.app_logger.info(msg='preparing to send pubsub message')

        pubsub_message = PubsubMessage(Metadata(publication_timestamp=int(time.time()),
                                                topic_name=PubsubMessage.TOPIC_NAME),
                                       Aggregate(id=str(uuid.uuid4()),
                                                 state='created',
                                                 business_entity=PubsubMessage.TOPIC_NAME,
                                                 aggregate_version=int(time.time()),
                                                 type=PubsubMessage.TYPE,
                                                 version='1.0',
                                                 gender=2,
                                                 location='all',
                                                 url=self.config['PUBSUB_NAMESPACE']))
        try:
            response = self.pubsub_service.send_message(pubsub_message=pubsub_message)
            if response.status_code is 202:
                self.app_logger.info(msg='pubsub successfully emitted')
                self.config['PUBSUB_EVENT_SENT'] = True
                return make_response({
                    'status': 'ok',
                    self.config.get('APP_NAME'): 'ready',
                    'response_code': 200})
        except Exception as ex:
            self.app_logger.error(msg=f'failed with error {traceback.format_exc()}',)

        return make_response({
            'status': 'pubsub failed',
            self.config.get('APP_NAME'): 'ready',
            'response_code': 200})
