# geocat.ch link checker
Version using AWS python SDK boto3 locally to use AWS SES service.

### Log into AWS SES service
boto3 needs AWS access key and secret access key from user with at least `AmazonSESFullAccess` permission.\
Those crendentials need to be given as environment variables :
```bash
AWS_ACCESS_KEY=foo
AWS_SECRET_ACCESS_KEY=foo
```
