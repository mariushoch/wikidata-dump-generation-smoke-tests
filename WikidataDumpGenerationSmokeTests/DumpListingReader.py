from urllib.request import urlopen
import datetime
import re
from typing import NamedTuple, Optional

try:
    class DumpMainInfo(NamedTuple):
        latest: dict[str, datetime.datetime]
        dirs: list[str]
    class DumpInfo(NamedTuple):
        size: int
        date: datetime.datetime
    class DumpDirInfo(NamedTuple):
        dumps: dict[str, DumpInfo]
        md5sums_file: Optional[str]
        sha1sums_file: Optional[str]
    class DumpAllInfo(NamedTuple):
        latest: dict[str, datetime.datetime]
        dump_dirs: dict[str, DumpDirInfo]
except TypeError:
    # B/C for Python < 3.9: https://docs.python.org/3.9/whatsnew/3.9.html#type-hinting-generics-in-standard-collections
    from collections import namedtuple
    DumpMainInfo = namedtuple('DumpMainIndex', ['latest', 'dirs'])
    DumpDirInfo = namedtuple('DumpDirInfo', ['dumps', 'md5sums_file', 'sha1sums_file'])
    DumpInfo = namedtuple('DumpInfo', ['size', 'date'])
    DumpAllInfo = namedtuple('DumpAllInfo', ['latest', 'dump_dirs'])

class DumpListingReader():
    main_index_url = None

    def __init__(self, main_index_url):
        self.main_index_url = main_index_url

    def _request_dump_main_index(self):
        with urlopen(self.main_index_url) as request:
            assert request.status == 200
            return request.read()

    def _request_dump_dir(self, dir_date):
        with urlopen(self.main_index_url + dir_date) as request:
            assert request.status == 200
            return request.read()

    def _get_dump_main_index(self) -> DumpMainInfo:
        dump_main_index_raw = self._request_dump_main_index()

        dirs = []
        latest = {}

        for line in dump_main_index_raw.splitlines():
            line = line.decode('UTF-8')
            res_dirs = re.search(r"20[2-3]\d[0-1]\d[0-3]\d/", line)
            res_latest = re.search(r"(latest-.*?\.(gz|bz2)).*(\d\d-\w{3}-20[2-3]\d)", line)
            if res_dirs:
                dirs.append(res_dirs.group(0))
            elif res_latest:
                date = datetime.datetime.strptime(res_latest.group(3), '%d-%b-%Y')
                latest[res_latest.group(1)] = date

        return DumpMainInfo(latest, dirs)

    def _get_dump_dir(self, dir_date) -> DumpDirInfo:
        dump_dir_raw = self._request_dump_dir(dir_date)
        dumps = {}
        md5sums_file = None
        sha1sums_file = None

        for line in dump_dir_raw.splitlines():
            line = line.decode('UTF-8')
            res_dump = re.search(r"((wikidata|commons)-.*?\.(gz|bz2)).*(\d\d-\w{3}-20[2-3]\d).*?(\d\d\d\d+)", line)
            res_hashsum_file = re.search(r"((wikidata|commons)-\d+-(sha1|md5)sums\.txt)", line)
            if res_dump:
                date = datetime.datetime.strptime(res_dump.group(4), '%d-%b-%Y')
                dump_info = DumpInfo(int(res_dump.group(5)), date)
                dumps[res_dump.group(1)] = dump_info
            elif res_hashsum_file:
                hash_type = res_hashsum_file.group(3)
                if hash_type == 'sha1':
                    sha1sums_file = res_hashsum_file.group(1)
                elif hash_type == 'md5':
                    md5sums_file = res_hashsum_file.group(1)
                else:
                    raise Exception('Unknown hash_type ' + hash_type)

        return DumpDirInfo(dumps, md5sums_file, sha1sums_file)

    def get_dumps_info(self) -> DumpAllInfo:
        dump_dirs = {}
        main_index = self._get_dump_main_index()

        for dir_date in main_index.dirs:
            dump_dirs[dir_date] = self._get_dump_dir(dir_date)

        return DumpAllInfo(main_index.latest, dump_dirs)
