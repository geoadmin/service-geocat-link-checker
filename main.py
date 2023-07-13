import os
import ssl
from smtplib import SMTP
import requests
from dotenv import load_dotenv
import settings
import utils
import link_checker

load_dotenv()

logger = utils.setup_logger(__name__)

headers = {"accept": "application/json", "Content-Type": "application/json"}

response = requests.get(url = f"{settings.HOST}/geonetwork/srv/api/groups",
                        headers=headers, timeout=10)

if response.status_code != 200:
    raise Exception("Cannot retrieve group information")


for group in response.json():

    logger.info("Processing group : %s", group["name"])

    indexes = utils.get_index(in_groups=[group["id"]])
    receiver = group["email"]

    # list of tested URL that are valid
    # We do not test them again
    valid_url = []

    report = []

    count = 0

    for index in indexes:

        result, new_valid_url = link_checker.check_metadata_url(index=index,
                                                     valid_url=valid_url)

        report.append(result)
        valid_url += new_valid_url

        count += 1
        logger.info("metadata processed : %s - %s%%", index["_source"]["uuid"],
                    round((count / len(indexes)) * 100, 1))

    if len([i for i in report if len(i["errors"]) > 0]) > 0:
        message = link_checker.get_message(report=report, receiver=receiver)

        host = os.environ.get("SMTP_ENDPOINT")
        port = os.environ.get("SMTP_PORT")
        user = os.environ.get("SMTP_USER")
        password = os.environ.get("SMTP_PASSWORD")

        context = ssl.create_default_context()

        with SMTP(host,port) as server :
            try:
                server.starttls(context=context)
                server.login(user=user, password=password)
                server.sendmail(settings.MAIL_SENDER, receiver, message.as_string())

            except Exception as e:
                logger.exception(e)

            else:
                logger.info("Group : %s - Mail sent", group["name"])

    else:
        logger.info("Group : %s - has no invalid URL", group["name"])
