from typing import List, Dict

import logging
import boto3
from dataclasses import dataclass

import pandas as pd

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

class QuotaChecker:
    """ Handle aws's resources to build sagemaker inference pipeline.

    Args:
        aws_access_key_id:
            - AWS_ACCESS_KEY_ID
        aws_secret_access_key:
            - AWS_SECRET_ACCESS_KEY
        region_name:
            - REGION_NAME (default : ap-northeast-2)

    Attributes:
        qt_client:
            - boto3's client api for handling s3 resources.
    """
    def __init__(
        self, 
        aws_access_key_id=None, 
        aws_secret_access_key=None, 
        region_name="ap-northeast-2",
    ):
        self.aws_configs = AwsBaseConfig(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )

        self.qt_client = boto3.client('service-quotas', **self.aws_configs.credentials)

    
    def check_service_code_list(self) -> List[Dict]:
        """ Check ServiceCode and ServiceName."""
        lists = self.qt_client.get_paginator('list_services')

        service_code_list = []
        for page in lists.paginate(MaxResults=100):
            service_code_list += page['Services']

        return service_code_list

    def check_quota_code_list(self, service_code: str) -> List[Dict]:
        """ Check QuotaCode and QuotaName."""
        lists = self.qt_client.get_paginator('list_service_quotas')

        quota_code_list = []
        for page in lists.paginate(ServiceCode=service_code, MaxResults=100):
            quota_code_list += page['Quotas']

        return quota_code_list

    def get_sagemaker_quotas_limits(self) -> pd.DataFrame:
        """Get available quotas and limits for sagemaker."""
        quota_code_list = self.check_quota_code_list('sagemaker')

        available_quotas_list = [{
            "RESOURCE":info['UsageMetric']['MetricDimensions']['Resource'],
            "DESCRIPTION":info['QuotaName'],
            "CURRNET_LIMIT":info['Value']
        }
            for info in quota_code_list if info.get('UsageMetric') != None]
        
        df = pd.DataFrame(available_quotas_list).sort_values('RESOURCE').reset_index(drop=True)
        return df

