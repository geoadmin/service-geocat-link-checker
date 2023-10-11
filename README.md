# geocat.ch link checker
This version use SMTP service to send email.

## SSL Certificate
When you are working with a custom python environment (not the standard one installed at swisstopo),
make sure to copy the SSL certificate from the standard environment to the custom one. The SSL certificate is used by requests to make call to https.

How to know where the certificate is in the default environment
```
& "c:/Program Files/ArcGIS/Pro/bin/Python/envs/arcgispro-py3/python.exe"

from certifi import where
where()
```
Overwrite the `cacert.pem` file into the custom python environment. Usually `your-env/Lib/site-packages/certifi/cacert.pem`

### SMTP Mail Server Hostname
You can pass SMTP hostname in environment variables
```bash
SMTP_ENDPOINT=foo
```
