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
    "track_total_hits": True,
    "sort": {"_id": "asc"},
    "size": 3000
}

GET_MD_INDEX_API_BODY = {
    "query": {
        "bool": {
            "must": [
                {
                    "multi_match": {
                        "query": None,
                        "fields": [
                            "id",
                            "uuid"
                        ]
                    }
                },
                {
                    "terms": {
                        "isTemplate": [
                            "n",
                            "y"
                        ]
                    }
                }
            ]
        }
    }
}

MAIL_SENDER = "geocat@swisstopo.ch"

MAIL_SUBJECT = "geocat.ch - Invalid URL in your metadata"

MAIL_BODY_START_TEXT = """
Hello,

While accessing the following URL, we found some unexcepted behaviour.
Please check if those URL are still available and fix them if necessary.

Thank you for your collaboration.
The geocat.ch team

----------

"""

MAIL_BODY_START_HTML = """
<html>
  <body>
    <p>Hello<br><br>
        While accessing the following URL, we found some unexcepted behaviour.<br>
        Please check if those URL are still available and fix them if necessary.<br><br>
       Thank you for your collaboration.<br>
       The geocat.ch team<br><br>
       ----------<br><br>
"""
