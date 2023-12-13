# geocat.ch link checker
This version use SMTP service w/o credentials (username & password) to send email.

The link checker fetches all published metadata index (grouped by metadata owner) and check the following URL:
* Contact website (currently indexed only in the main language)
* Every online resources link (in all available languages)

If metadata contains invalid URL, an email is sent to the metadata owner with a list of invalid URL.

## Installation
Clone the repo and install dependencies in a python virtual environment
```
git clone https://github.com/geoadmin/service-geocat-link-checker.git

cd service-geocat-link-checker

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

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

## SMTP Mail Server Hostname
You can pass SMTP hostname in environment variables in a `.env` file
```bash
SMTP_ENDPOINT=foo
```
## Login geocat.ch
Since the link checker fetches information about geocat.ch users (id, email adress), it needs login credentials with administrator profile. The credentials can be pass in a `.env` file :
```bash
GEOCAT_USERNAME=foo
GEOCAT_PASSWORD=foo
```

## URL White List
In the `config.py` file, it is possible to specify URL that have to be considered valid. The latter won't be checkek by the process. This is useful e.g. for intranet and protected URL.
```python
# It uses Regex, for exact match use : ^{url}$ 

URL_WHITE_LIST = [
    "^https://map.georessourcen.ethz.ch/$",
    "^https://oereb.llv.li/$",
    "^http://mapplus/.*",
    "^http://sparcgis01.ad.net.fr.ch/.*"
]
```
