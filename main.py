import os
import sys
from smtplib import SMTP
import requests
from dotenv import load_dotenv
import config
import utils
import logging
import logging.config
from datetime import datetime

logs_dir = os.path.join(os.path.dirname(__file__), "logs")

if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

logfile = f"{datetime.now().strftime('%Y%m%d%H%M%S')}.log"

log_config = utils.get_log_config(os.path.join(logs_dir, logfile))
logging.config.dictConfig(log_config)

import link_checker

load_dotenv()

logger = logging.getLogger(__name__)

headers = {"accept": "application/json", "Content-Type": "application/json"}

for proxies in config.PROXY:
    try:
        response = requests.get(url = f"{config.HOST}/geonetwork/srv/api/groups",
                        headers=headers, timeout=10, proxies=proxies)
    except Exception as e:
        print(e)
    else:
        os.environ["HTTP_PROXY"] = proxies["http"]
        os.environ["HTTPS_PROXY"] = proxies["https"]
        break

try:
    response
except NameError:
    logger.error("Cannot retrieve group information - group request failed")
    sys.exit()
else:
    if response.status_code != 200:
        logger.error("Cannot retrieve group information - group request bad status")
        sys.exit()

for group in response.json()[1:2]:

    logger.info("Processing group : %s", group["name"])

    try:
        indexes = utils.get_index(in_groups=[group["id"]])
    except:
        logger.error("Processing group : %s : couldn't fetch metadata index", group["name"])
        continue

    # For test purpose, send email only to the sender
    # receivers = [group["email"], config.MAIL_SENDER]
    receivers = [config.MAIL_SENDER]

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
        message = link_checker.get_message(report=report, receiver=receivers[0])

        host = os.environ.get("SMTP_ENDPOINT")

        try:
            with SMTP(host) as server:
                server.sendmail(config.MAIL_SENDER, receivers, message.as_string())

        except Exception as e:
            logger.exception(e)

        else:
            logger.info("Group : %s - Mail sent", group["name"])

    else:
        logger.info("Group : %s - has no invalid URL", group["name"])
