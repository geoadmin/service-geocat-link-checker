# geocat.ch link checker 
This version use SMTP service w/o credentials (username & password) to send email.

## SSL Certificate
When you are working with a custom python environment (not the standard one installed at swisstopo),
make sure to copy the SSL certificate from the standard environment to the custom one. The SSL certificate is used by requests to make call to https.

How to know where the certificate is in the default environment
```
& "c:/Program Files/ArcGIS/Pro/bin/Python/envs/arcgispro-py3/python.exe"

from certifi import where
where()
```
Overwrite the `cacert.pem` file into the custom python environment, usually `your-env/Lib/site-packages/certifi/cacert.pem`, by the one found on the default environment.

### SMTP Mail Server Hostname
You can pass SMTP hostname in environment variables in a .env file
```bash
SMTP_ENDPOINT=foo
```
