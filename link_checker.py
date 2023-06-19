import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from http import HTTPStatus
import time
import requests
import settings
import utils

if __name__ in logging.Logger.manager.loggerDict.keys():
    logger = logging.getLogger(__name__)
else:
    logger = utils.setup_logger(__name__)


def __url_checker(url: str, allow_redirects: bool = True) -> bool:
    """Check if URL is valid"""

    RETRY = 5

    RETRY_CODE = [
        HTTPStatus.TOO_MANY_REQUESTS,
        HTTPStatus.INTERNAL_SERVER_ERROR,
        HTTPStatus.BAD_GATEWAY,
        HTTPStatus.SERVICE_UNAVAILABLE,
        HTTPStatus.GATEWAY_TIMEOUT,
    ]

    for i in range(RETRY):

        try:
            response = requests.get(url=url, allow_redirects=allow_redirects, timeout=30)
            response.raise_for_status()

        except requests.exceptions.HTTPError as exc:

            code = exc.response.status_code

            if code in RETRY_CODE:
                logger.warning("checking URL (try %s) : %s - %s", i+1, url, repr(exc))
                # retry after n seconds
                time.sleep((i+1)**2)
                continue

            else:
                logger.error("Invalid URL : %s - %s", url, repr(exc))
                return False

        except requests.exceptions.ConnectionError as exc:

            logger.warning("checking URL (try %s) : %s - %s", i+1, url, repr(exc))
            time.sleep(i**2 + 1)
            continue

        except requests.exceptions.RequestException as exc:

            logger.error("Invalid URL : %s - %s", url, repr(exc))
            return False

        else:
            return True

    logger.error("Invalid URL : %s", url)
    return False


def check_metadata_url(index: dict, valid_url: list) -> dict:
    """Check if URL of metadata are valid"""

    result = {
        "uuid": index["_source"]["uuid"], 
        "title": index["_source"]["resourceTitleObject"]["default"], 
        "errors": list()        
    }

    new_valid_url = []

    # Other constraints Link    
    if "MD_LegalConstraintsOtherConstraintsObject" in index["_source"]:
        for i in index["_source"]["MD_LegalConstraintsOtherConstraintsObject"]:
            if "link" in i:
                if i["link"] not in valid_url:
                    if not __url_checker(i["link"]):
                        result["errors"].append(
                            {
                                "url": i["link"],
                                "location": "Other Constraints"
                            }
                        )
                    else:
                        new_valid_url.append(i["link"])
                        valid_url.append(i["link"])

    # Website for contacts
    for contact in ["contact", "contactForResource", "contactForDistribution"]:

        if contact in index["_source"]:
            for i in index["_source"][contact]:
                if "website" in i:
                    if i["website"] not in valid_url:
                        if i["website"] != "":
                            if not __url_checker(i["website"]):
                                result["errors"].append(
                                    {
                                        "url": i["website"],
                                        "location": f"Website of {contact}"
                                    }
                                )
                            else:
                                new_valid_url.append(i["website"])
                                valid_url.append(i["website"])

    # Resources Link
    if "link" in index["_source"]:
        for i in index["_source"]["link"]:
            if i["protocol"].startswith(("OGC:WMS", "OGC:WMTS", "OGC:WFS")):
                for url in set(i["urlObject"].values()):
                    if url not in valid_url:
                        if not __url_checker(url, allow_redirects=False):

                            result["errors"].append(
                                {
                                    "url": url,
                                    "location": f"Online resource URL with {i['protocol']} protocol (redirect not allowed for geoservices)"
                                }
                            )

                        else:
                            new_valid_url.append(url)
                            valid_url.append(url)
            else:
                for url in set(i["urlObject"].values()):
                    if url not in valid_url:
                        if not __url_checker(url):

                            if i['protocol'] == "":
                                i['protocol'] = "missing"

                            result["errors"].append(
                                {
                                    "url": url,
                                    "location": f"Online resource URL with {i['protocol']} protocol"
                                }
                            )
                        else:
                            new_valid_url.append(url)
                            valid_url.append(url)

    return result, new_valid_url


def get_message(report: list, receiver: str) -> object:
    """Creates an email message object"""

    message = MIMEMultipart("alternative")
    message["Subject"] = settings.MAIL_SUBJECT
    message["From"] = settings.MAIL_SENDER
    message["To"] = receiver

    body_text = settings.MAIL_BODY_START_TEXT
    body_html = settings.MAIL_BODY_START_HTML

    for metadata in [i for i in report if len(i["errors"]) > 0]:

        body_text += f"Dataset: {settings.URL_METADATA}{metadata['uuid']}\n\n"
        body_html += f"Dataset: <a href='{settings.URL_METADATA}{metadata['uuid']}'>{metadata['title']}</a><br><br>"

        for error in metadata["errors"]:

            body_text += f"Invalid URL: {error['url']}\n"
            body_text += f"Location: {error['location']}\n\n"

            body_html += f"Invalid URL: <a href='{error['url']}'>{error['url']}</a><br>"
            body_html += f"Location: {error['location']}<br><br>"            

        body_text += "-----\n\n"
        body_html += "-----<br><br>"

    body_html += "</p></body></html>"

    part1 = MIMEText(body_text, "plain")
    part2 = MIMEText(body_html, "html")

    message.attach(part1)
    message.attach(part2)

    return message
