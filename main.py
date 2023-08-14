import os
import ssl
from smtplib import SMTP
import requests
from dotenv import load_dotenv
import config
import utils
import urllib3
import logging
from logging import config as loggingconfig
from datetime import datetime
import link_checker

load_dotenv()

if not os.path.exists("logs"):
    os.makedirs("logs")

logfile = f"{datetime.now().strftime('%Y%m%d%H%M%S')}.log"

# log_config = utils.get_log_config(os.path.join("logs", logfile))
# loggingconfig.dictConfig(log_config)
# logger = logging.getLogger(__name__)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", '%Y-%m-%d %H:%M:%S')

handler = logging.StreamHandler()
handler.setLevel("INFO")
handler.setFormatter(formatter)

fileHandler = logging.FileHandler(os.path.join("logs", logfile))
fileHandler.setLevel("INFO")
fileHandler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.handlers.clear()

logger.setLevel("INFO")
logger.addHandler(handler)
logger.addHandler(fileHandler)

headers = {"accept": "application/json", "Content-Type": "application/json"}

for proxies in config.PROXY:
    try:
        response = requests.get(url = f"{config.HOST}/geonetwork/srv/api/groups",
                        headers=headers, timeout=10, proxies=proxies)
    except (requests.exceptions.ProxyError, OSError, urllib3.exceptions.MaxRetryError):
        pass
    else:
        os.environ["HTTP_PROXY"] = proxies["http"]
        os.environ["HTTPS_PROXY"] = proxies["https"]
        break

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

        try:
            with SMTP(host,port) as server:
                server.starttls(context=context)
                server.login(user=user, password=password)
                server.sendmail(config.MAIL_SENDER, receiver, message.as_string())

        except Exception as e:
            logger.exception(e)

        else:
            logger.info("Group : %s - Mail sent", group["name"])

    else:
        logger.info("Group : %s - has no invalid URL", group["name"])
