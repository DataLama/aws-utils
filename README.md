# aws-utils
aws 사용할 때, 유용한 스크립트 모음 (boto3 사용)

## scripts

### [check_aws_quotas](scripts/check_aws_quotas/README.md)


## Tips

### python에서 환경 변수로 저장된 aws credential load 하기.
- `.env` files
```
AWS_ACCESS_KEY_ID=XXXXXXX
AWS_SECRET_ACCESS_KEY=YYYYYYY
```

```python
import os
from dotenv import load_dotenv

load_dotenv()
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
```