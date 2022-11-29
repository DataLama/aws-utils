import logging
import boto3
import sagemaker
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass(repr=True)
class AwsBaseConfig:
    """ Setting AWS Base key, id, region and Make Credential dicts.
    Args:
        aws_access_key_id:
            - AWS_ACCESS_KEY_ID
        aws_secret_access_key:
            - AWS_SECRET_ACCESS_KEY
        region_name:
            - REGION_NAME (default : ap-northeast-2)
    Returns:
        AwsBaseConfig
    """
    aws_access_key_id: str
    aws_secret_access_key: str
    region_name: str
    credentials: dict

    def __init__(self, aws_access_key_id, aws_secret_access_key, region_name="ap-northeast-2"):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name
        self.credentials = {
                "aws_access_key_id": self.aws_access_key_id ,
                "aws_secret_access_key": self.aws_secret_access_key,
                "region_name": region_name
            }

class SageMakerBase:
    """ Handle aws's resources to build sagemaker inference pipeline.

    Args:
        aws_access_key_id:
            - AWS_ACCESS_KEY_ID
        aws_secret_access_key:
            - AWS_SECRET_ACCESS_KEY
        region_name:
            - REGION_NAME (default : ap-northeast-2)
        role_name:
            - suffix for sagemaker execution role
        sm_default_bucket:
            - default_bucket for sagemaker inference pipeline.

    Attributes:
        s3_client:
            - boto3's client api for handling s3 resources.
        sm_client:
            - boto3's client api for handling sagemaker resources.
        sm_session:
            - sagemaker session which is used for build sagemaker pipleine.
        role:
            - sagemaker execution role.
        
    """
    def __init__(
        self, 
        aws_access_key_id=None, 
        aws_secret_access_key=None, 
        region_name="ap-northeast-2",
        role_name=None,
        sm_default_bucket=None,
    ):
        self.aws_configs = AwsBaseConfig(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )

        self.s3_client = boto3.client("s3", **self.aws_configs.credentials)

        self.sm_client = boto3.client('sagemaker', **self.aws_configs.credentials)
        self.sm_session = sagemaker.session.Session(
            boto_session=boto3.Session(**self.aws_configs.credentials),
            sagemaker_client=self.sm_client,
            sagemaker_runtime_client=boto3.client("sagemaker-runtime", **self.aws_configs.credentials),
            default_bucket=sm_default_bucket,
        )

        self.account_id = boto3.client("sts", **self.aws_configs.credentials).get_caller_identity().get("Account")

        try:
            self.role = sagemaker.get_execution_role()
            logger.info(f"[*] Use instance's authorized sagemaker execution role. - {self.role}")
        except:
            self.role = f"arn:aws:iam::{self.account_id}:role/{role_name}"
            logger.info(f"[*] Use predefined sagemaker execution role. - {self.role}")