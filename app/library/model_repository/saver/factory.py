from app.errors import ApplicationException
from app.library.model_repository.saver.saver_interface import SaverInterface
from app.library.model_repository.saver.driver.filesystem import Filesystem
from app.library.model_repository.saver.driver.s3 import S3
from app.library.model_repository.repository import Repository
from app.config import Config
import boto3


class Factory:

    DRIVER_FILESYSTEM = 'Filesystem'
    DRIVER_S3 = 'S3'

    @staticmethod
    def factory(driver: str) -> SaverInterface:
        # Build filesystem saver
        if driver == Factory.DRIVER_FILESYSTEM:
            return Filesystem(Repository(Config.MODEL_BASE_DIR))

        # Build s3 saver
        if driver == Factory.DRIVER_S3:
            s3_client = boto3.client('s3',
                                     region_name=Config.AWS_REGION,
                                     aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                                     aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY)
            return S3(Repository(Config.MODEL_BASE_DIR_S3), s3_client, Config.AWS_S3_BUCKET)

        raise ApplicationException('Can not initialize a saver for driver {}'.format(driver))
