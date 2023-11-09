from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from http import HTTPStatus
import time
import requests
import config
import logging

logger = logging.getLogger(__name__)

def __url_checker(url: str, allow_redirects: bool = True) -> bool:
    """Check if URL is valid"""

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.76"
        }

    RETRY = 5

    RETRY_CODE = [
        HTTPStatus.TOO_MANY_REQUESTS,
        HTTPStatus.INTERNAL_SERVER_ERROR,
        HTTPStatus.BAD_GATEWAY,
        HTTPStatus.SERVICE_UNAVAILABLE,
        HTTPStatus.GATEWAY_TIMEOUT,
    ]

    PASS_CODE = [
        HTTPStatus.UNAUTHORIZED,
        HTTPStatus.FORBIDDEN,
    ]

    if url in config.URL_WHITE_LIST:
        return True

    for i in range(RETRY):

        try:
            with requests.get(url=url, allow_redirects=allow_redirects,
                                timeout=30, headers=headers, stream=True) as response:

                response.raise_for_status()

        except requests.exceptions.HTTPError as exc:

            code = exc.response.status_code

            if code in RETRY_CODE:
                logger.warning("checking URL (try %s) : %s - %s", i+1, url, repr(exc))
                # retry after n seconds
                time.sleep((i+1)**2)
                continue

            elif code in PASS_CODE:
                return True

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
    # if "MD_LegalConstraintsOtherConstraintsObject" in index["_source"]:
    #     for i in index["_source"]["MD_LegalConstraintsOtherConstraintsObject"]:
    #         if "link" in i:
    #             if i["link"] not in valid_url:
    #                 if not __url_checker(i["link"]):
    #                     result["errors"].append(
    #                         {
    #                             "url": i["link"],
    #                             "location": "Other Constraints"
    #                         }
    #                     )
    #                 else:
    #                     new_valid_url.append(i["link"])
    #                     valid_url.append(i["link"])

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

                                if not i["website"].lower().startswith("http"):
                                    result["errors"][-1]["location"] += " (URL schema e.g. https or http is perhaps missing)"

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

                            if not url.lower().startswith("http"):
                                result["errors"][-1]["location"] += " (URL schema e.g. https or http is perhaps missing)"

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

                            if not url.lower().startswith("http"):
                                result["errors"][-1]["location"] += " (URL schema e.g. https or http is perhaps missing)"

                        else:
                            new_valid_url.append(url)
                            valid_url.append(url)

    return result, new_valid_url


def get_message(report: list, receiver: str, group_label: str) -> object:
    """Creates an email message object"""

    message = MIMEMultipart("alternative")
    message["Subject"] = config.MAIL_SUBJECT + group_label
    message["From"] = config.MAIL_SENDER
    message["To"] = receiver
    message["X-Priority"] = "1"  # 1 (High), 3 (normal), 5 (Low)

    body_text = config.MAIL_BODY_START_TEXT
    body_html = config.MAIL_BODY_START_HTML

    for metadata in [i for i in report if len(i["errors"]) > 0]:

        body_text += f"Dataset: {config.URL_METADATA}{metadata['uuid']}\n\n"
        body_html += f"Dataset: <a href='{config.URL_METADATA}{metadata['uuid']}'>{metadata['title']}</a><br><br>"

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
