import datetime
import csv

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

GITHUB_API = "https://api.github.com"
REPO = "etalab/schema.data.gouv.fr"
PHASES = ["construction", "investigation"]


def requests_retry_session(
    retries=5,
    backoff_factor=1,
    status_forcelist=[401, 402, 403, 500, 502, 504],
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )

    adapter = HTTPAdapter(max_retries=retry)

    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


r = requests_retry_session().get("https://webconf.numerique.gouv.fr/stats/homePage")
r.raise_for_status()
data = r.json()

date = datetime.datetime.utcnow().isoformat()

hourly_data = {
    "date": date,
    "nb_conferences": data["conf"],
    "nb_participants": data["part"],
}

with open("data/data.csv", "a") as f:
    writer = csv.DictWriter(f, hourly_data, lineterminator="\n")
    if f.tell() == 0:
        writer.writeheader()
    writer.writerow(hourly_data)
