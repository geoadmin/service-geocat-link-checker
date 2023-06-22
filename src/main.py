import logging
import requests
import boto3
import settings
import utils
import link_checker


if __name__ in logging.Logger.manager.loggerDict.keys():
    logger = logging.getLogger(__name__)
else:
    logger = utils.setup_logger(__name__)

headers = {"accept": "application/json", "Content-Type": "application/json"}

response = requests.get(url = f"{settings.HOST}/geonetwork/srv/api/groups",
                        headers=headers, timeout=10)

if response.status_code != 200:
    raise Exception("Cannot retrieve group information")


for group in response.json()[1:2]:

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

        ses = boto3.client(
                "ses",
                region_name="eu-central-1"
            )

        try:
            ses.send_raw_email(
                Source=message['From'],
                Destinations=[receiver],
                RawMessage={
                    'Data': message.as_string()
                }
            )

        except Exception as exc:
            logger.error(repr(exc))

        else:
            logger.info("Group : %s - Mail sent", group["name"])

    else:
        logger.info("Group : %s - has no invalid URL", group["name"])
