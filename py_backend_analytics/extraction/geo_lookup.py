import gzip
import shutil
import tempfile
from pathlib import Path
from datetime import date
from urllib.request import urlopen

import maxminddb

from constants import (
    TEMP_DIR_NAME,
    MMDB_FILE_NAME,
    GZ_FILE_NAME,
    DBIP_URL,
    COUNTRY,
    NAMES,
    EN,
)


class IpCountryLookup:
    def __init__(self):
        self._dir = Path(tempfile.gettempdir()) / TEMP_DIR_NAME
        self._dir.mkdir(exist_ok=True)
        self._mmdb = self._dir / MMDB_FILE_NAME
        if not self._mmdb.exists():
            self._download()
        self._db = maxminddb.open_database(str(self._mmdb))

    def get_country(self, ip: str) -> str | None:
        data = self._db.get(ip)

        if not data:
            return None

        return data.get(COUNTRY, {}).get(NAMES, {}).get(EN)

    def _download(self):
        url = self._url()
        gz = self._dir / GZ_FILE_NAME

        with urlopen(url) as r:
            with open(gz, "wb") as f:
                f.write(r.read())

        with gzip.open(gz, "rb") as f_in:
            with open(self._mmdb, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

    def _url(self) -> str:
        month = date.today().strftime("%Y-%m")

        return DBIP_URL.format(month=month)
