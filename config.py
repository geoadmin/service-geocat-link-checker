PROXY = [
    {
        "http": "proxy-bvcol.admin.ch:8080",
        "https": "proxy-bvcol.admin.ch:8080",
    },
    {
        "http": "proxy.admin.ch:8080",
        "https": "proxy.admin.ch:8080",
    },
    {
        "http": "prxp01.admin.ch:8080",
        "https": "prxp01.admin.ch:8080",
    },
    {
        "http": "prp01.adb.intra.admin.ch",
        "https": "prp01.adb.intra.admin.ch",
    },   
    {}
]

HOST = "https://www.geocat.ch"

URL_METADATA = f"{HOST}/geonetwork/srv/eng/catalog.search#/metadata/"

NS = {
    'csw': 'http://www.opengis.net/cat/csw/2.0.2',
    'gco': 'http://www.isotc211.org/2005/gco',
    'che': 'http://www.geocat.ch/2008/che',
    'gmd': 'http://www.isotc211.org/2005/gmd',
    'srv': 'http://www.isotc211.org/2005/srv',
    'gmx': 'http://www.isotc211.org/2005/gmx',
    'gts': 'http://www.isotc211.org/2005/gts',
    'gsr': 'http://www.isotc211.org/2005/gsr',
    'gmi': 'http://www.isotc211.org/2005/gmi',
    'gml': 'http://www.opengis.net/gml/3.2',
    'xlink': 'http://www.w3.org/1999/xlink',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    'geonet': 'http://www.fao.org/geonetwork',
    'java': 'java:org.fao.geonet.util.XslUtil',
}

LANG_ISO = {
    "ger": "DE",
    "fre": "FR",
    "ita": "IT",
    "eng": "EN",
    "roh": "RM"
}

SEARCH_UUID_API_BODY = {
    "from": 0,
    "query": {
        "bool": {
            "must": []
        }
    },
    "_source": {
        "includes": [
            "uuid",
            "resourceTitleObject",
            "MD_LegalConstraintsOtherConstraintsObject",
            "contact",
            "contactForResource",
            "contactForDistribution",
            "link"
        ]
    },
    "track_total_hits": True,
    "sort": {"_id": "asc"},
    "size": 3000
}

MAIL_SENDER = "geocat@swisstopo.ch"

MAIL_SUBJECT = "geocat.ch - Invalid URL in your metadata"

MAIL_BODY_START_TEXT = """
Hello,

While accessing the following URL, we found some unexpected behaviour.
Please check if those URL are still available and fix them if necessary.

PS: HTTPS or HTTP schema is mandatory for all URL in geocat.ch.

Thank you for your collaboration.
The geocat.ch team

----------

"""

MAIL_BODY_START_HTML = """
<html>
  <body>
    <p>Hello<br><br>
        While accessing the following URL, we found some unexpected behaviour.<br>
        Please check if those URL are still available and fix them if necessary.<br><br>
        PS: HTTPS or HTTP schema is mandatory for all URL in geocat.ch.<br><br>
       Thank you for your collaboration.<br>
       The geocat.ch team<br><br>
       ----------<br><br>
"""
