import json
import logging
import xml.etree.ElementTree as ET
import copy
import requests
import config


def xpath_ns_url2code(path: str) -> str:
    """Replace the namespace url by the namespace acronym in the given xpath"""
    for key in config.NS:
        path = path.replace("{" + config.NS[key] + "}", f"{key}:")

    return path


def xpath_ns_code2url(path: str) -> str:
    """Replace the namespace url by the namespace acronym in the given xpath"""
    for key in config.NS:
        path = path.replace(f"{key}:", "{" + config.NS[key] + "}")

    return path


def setup_logger(name: str, logfile: str, level=logging.INFO) -> object:
    """Setup a logger for logging

    Args:
        name: required, the mane of the logger
        level: optional, the level to log

    Returns:
        Logger object
    """
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", '%Y-%m-%d %H:%M:%S')

    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(formatter)

    fileHandler = logging.FileHandler(logfile)
    fileHandler.setLevel(level)
    fileHandler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.addHandler(fileHandler)

    return logger


def get_log_config(logfile: str):
    return {
    "version":1,
    "root":{
        "handlers" : ["console", "file"],
        "level": "INFO"
    },
    "handlers":{
        "console":{
            "formatter": "std_out",
            "class": "logging.StreamHandler",
            "level": "INFO"
        },
        "file":{
            "formatter": "std_out",
            "class": "logging.FileHandler",
            "level": "INFO",
            "filename": logfile
        }   
    },
    "formatters":{
        "std_out": {
            "format": "%(asctime)s - %(levelname)s - %(message)s",
            "datefmt":"%Y-%m-%d %H:%M:%S"
        }
    },
}


def okgreen(text):
    return f"\033[92m{text}\033[00m"


def warningred(text):
    return f"\033[91m{text}\033[00m"


def process_ok(response) -> bool:
    """
    Process the response of the geocat API requests.

    Works for following requests :
     - /{portal}/api/records/batchediting
     - /{portal}/api/records/validate
     - /{portal}/api/records/{metadataUuid}/ownership

    Args:
        response:
            object, required, the response object of the API request

    Returns:
        boolean: True if the process was successful, False if not
    """
    if response.status_code == 201:
        r_json = json.loads(response.text)
        if len(r_json["errors"]) == 0 and r_json["numberOfRecordNotFound"] == 0 \
        and r_json["numberOfRecordsNotEditable"] == 0 and r_json["numberOfNullRecords"] == 0 \
        and r_json["numberOfRecordsWithErrors"] == 0 and r_json["numberOfRecordsProcessed"] == 1:
            return True
        else:
            return False
    else:
        return False


def get_metadata_languages(metadata: bytes) -> dict:
    """
    Fetches all languages of the metadata (given as bytes string).
    Returns main and additonal metadata languages in form of a dictionnary.
    """

    languages = {
        "language": None,
        "locales": list(),
    }

    xml_root = ET.fromstring(metadata)

    languages["language"] = xml_root.find("./gmd:language/gmd:LanguageCode",
                    namespaces=config.NS).attrib["codeListValue"]

    for lang in xml_root.findall("./gmd:locale//gmd:LanguageCode", namespaces=config.NS):
            if lang.attrib["codeListValue"] != languages["language"] and \
                lang.attrib["codeListValue"] not in languages["locales"]:

                languages["locales"].append(lang.attrib["codeListValue"])

    return languages


def xmlify(string: str) -> str:
    """Replace XML special characters"""

    string = string.replace("&", "&amp;")
    string = string.replace(">", "&gt;")
    string = string.replace("<", "&lt;")
    string = string.replace("'", "&apos;")
    string = string.replace('"', "&quot;")

    return string


def __search_md_index(body: dict) -> list:
    """
    Performs deep paginated search using ES search API request.
    Args: body, the request's body
    """

    md_index = []

    headers = {"accept": "application/json", "Content-Type": "application/json"}

    body = json.dumps(body)

    while True:

        response = requests.post(url=f"{config.HOST}/geonetwork/srv/api/search/records/_search",
                                 headers=headers, data=body, timeout=300)

        response.raise_for_status()

        if response.status_code == 200:
            for hit in response.json()["hits"]["hits"]:
                md_index.append(hit)

            body = json.loads(body)
            if len(response.json()["hits"]["hits"]) < body["size"]:
                break

            body["search_after"] = response.json()["hits"]["hits"][-1]["sort"]
            body = json.dumps(body)

        else:
            break

    return md_index


def get_index(with_harvested: bool = True, valid_only: bool = False, published_only:
                bool = False, with_templates: bool = False, in_groups: list = None,
                not_in_groups: list = None, keywords: list = None, q: str = None) -> list:
    """
    Get a list of metadata index.
    You can specify if you want or not : harvested, valid, published records and templates.
    """

    body = copy.deepcopy(config.SEARCH_UUID_API_BODY)

    if with_templates:
        body["query"]["bool"]["must"].append({"terms": {"isTemplate": ["y", "n"]}})
    else:
        body["query"]["bool"]["must"].append({"terms": {"isTemplate": ["n"]}})

    query_string = str()

    if not with_harvested:
        query_string = query_string + "(isHarvested:\"false\") AND"

    if valid_only:
        query_string = query_string + "(valid:\"1\") AND"

    if published_only:
        query_string = query_string + "(isPublishedToAll:\"true\") AND"

    if in_groups is not None:
        toadd = " OR ".join([f"groupOwner:\"{i}\"" for i in in_groups])
        query_string = query_string + f"({toadd}) AND"

    if not_in_groups is not None:
        toadd = " OR ".join([f"-groupOwner:\"{i}\"" for i in not_in_groups])
        query_string = query_string + f"({toadd}) AND"

    if keywords is not None:
        query_kw = " OR ".join([f"tag.default:\"{i}\" OR tag.langfre:\"{i}\"" \
            f"OR tag.langger:\"{i}\" OR tag.langita:\"{i}\" OR tag.langeng:\"{i}\""
            for i in keywords])

        query_string = query_string + f"({query_kw}) AND"

    if q is not None:
        query_string = query_string + f"({q}) AND"

    if len(query_string) > 0:
        query_string = query_string[:-4]
        body["query"]["bool"]["must"].insert(0, {"query_string": {"query": query_string,
                "default_operator": "AND"}})

    return __search_md_index(body=body)
