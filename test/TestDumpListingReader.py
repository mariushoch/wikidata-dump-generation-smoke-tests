import sys
import os
sys.path.insert(1, os.path.realpath(os.path.pardir))

import unittest
from unittest.mock import patch
from pathlib import Path
from WikidataDumpGenerationSmokeTests import DumpListingReader
from WikidataDumpGenerationSmokeTests.DumpListingReader import DumpInfo
from datetime import datetime

__DIR__ = os.path.dirname(os.path.abspath(__file__))
wikidatawiki20211030_dirs = [
    '20210915/',
    '20210917/',
    '20210920/',
    '20210922/',
    '20210924/',
    '20210927/',
    '20210929/',
    '20211001/',
    '20211004/',
    '20211006/',
    '20211008/',
    '20211011/',
    '20211013/',
    '20211015/',
    '20211018/',
    '20211020/',
    '20211022/',
    '20211025/',
    '20211027/',
    '20211029/'
]

class TestDumpListingReader(unittest.TestCase):
    @patch('WikidataDumpGenerationSmokeTests.DumpListingReader._request_dump_main_index')
    def test_get_dump_main_index_empty(self, mock_request_dump_main_index):
        mock_request_dump_main_index.side_effect = lambda : 'foo'.encode()

        dump_listing_reader = DumpListingReader('')
        dump_main_index = dump_listing_reader._get_dump_main_index()
        self.assertEqual(dump_main_index.latest, {})
        self.assertEqual(dump_main_index.dirs, [])

    @patch('WikidataDumpGenerationSmokeTests.DumpListingReader._request_dump_dir')
    @patch('WikidataDumpGenerationSmokeTests.DumpListingReader._request_dump_main_index')
    def test_get_dump_main_index_wikidatawiki20211030(self, mock_request_dump_main_index, mock_request_dump_dir):
        mock_request_dump_main_index.side_effect = lambda : Path(__DIR__ + '/DumpListingReaderTestCases/wikidatawiki-2021-10-30/index.html').read_text().encode()
        mock_request_dump_dir.side_effect = ''.encode()

        dump_listing_reader = DumpListingReader('')
        dump_main_index = dump_listing_reader._get_dump_main_index()
        self.assertEqual(len(dump_main_index.latest), 14)
        self.assertEqual(dump_main_index.dirs, wikidatawiki20211030_dirs)
        # Just check two "latest" dumps by example
        self.assertEqual(dump_main_index.latest['latest-all.json.bz2'], datetime.fromisoformat('2021-10-28'))
        self.assertEqual(dump_main_index.latest['latest-truthy.nt.gz'], datetime.fromisoformat('2021-10-30'))

    @patch('WikidataDumpGenerationSmokeTests.DumpListingReader._request_dump_dir')
    def test_get_dump_dir_wikidatawiki20211030_20210924(self, mock_request_dump_dir):
        def request_dump_dir_from_file(dir_date):
            self.assertEqual(dir_date, '20210924/')
            dir_date = dir_date.replace('/', '')
            return Path(
                    __DIR__ + '/DumpListingReaderTestCases/wikidatawiki-2021-10-30/index-' + dir_date + '.html'
                ).read_text().encode()

        mock_request_dump_dir.side_effect = request_dump_dir_from_file

        dump_listing_reader = DumpListingReader('')
        dump_dir = dump_listing_reader._get_dump_dir('20210924/')

        self.assertEqual(dump_dir.dumps, {
            'wikidata-20210924-lexemes-BETA.nt.bz2': DumpInfo(512902814, datetime.fromisoformat('2021-09-24')),
            'wikidata-20210924-lexemes-BETA.nt.gz': DumpInfo(697520557, datetime.fromisoformat('2021-09-24')),
            'wikidata-20210924-lexemes-BETA.ttl.bz2': DumpInfo(277698476, datetime.fromisoformat('2021-09-24')),
            'wikidata-20210924-lexemes-BETA.ttl.gz':DumpInfo(354761658, datetime.fromisoformat('2021-09-24')),
        })
        self.assertEqual(dump_dir.md5sums_file, 'wikidata-20210924-md5sums.txt')
        self.assertEqual(dump_dir.sha1sums_file, 'wikidata-20210924-sha1sums.txt')

    @patch('WikidataDumpGenerationSmokeTests.DumpListingReader._request_dump_dir')
    @patch('WikidataDumpGenerationSmokeTests.DumpListingReader._request_dump_main_index')
    def test_get_dumps_info_wikidatawiki20211030(self, mock_request_dump_main_index, mock_request_dump_dir):
        dump_dirs_to_visit = wikidatawiki20211030_dirs.copy()

        def request_dump_dir(dir_date):
            self.assertIn(dir_date, dump_dirs_to_visit)
            dump_dirs_to_visit.remove(dir_date)
            dir_date = dir_date.replace('/', '')
            return Path(
                    __DIR__ + '/DumpListingReaderTestCases/wikidatawiki-2021-10-30/index-' + dir_date + '.html'
                ).read_text().encode()

        mock_request_dump_main_index.side_effect = lambda : Path(__DIR__ + '/DumpListingReaderTestCases/wikidatawiki-2021-10-30/index.html').read_text().encode()
        mock_request_dump_dir.side_effect = request_dump_dir

        dump_listing_reader = DumpListingReader('')
        dumps_info = dump_listing_reader.get_dumps_info()
        self.assertEqual(len(dumps_info.latest), 14)
        self.assertEqual(len(dumps_info.dump_dirs), len(wikidatawiki20211030_dirs))
        # Just check one by example
        dump_dir = dumps_info.dump_dirs['20211006/']
        self.assertEqual(dump_dir.dumps, {
            'wikidata-20211006-lexemes.json.bz2': DumpInfo(195288101, datetime.fromisoformat('2021-10-06')),
            'wikidata-20211006-lexemes.json.gz': DumpInfo(271807724, datetime.fromisoformat('2021-10-06')),
            'wikidata-20211006-truthy-BETA.nt.bz2': DumpInfo(30708742696, datetime.fromisoformat('2021-10-09')),
            'wikidata-20211006-truthy-BETA.nt.gz': DumpInfo(50187553542, datetime.fromisoformat('2021-10-09')),
        })
        self.assertEqual(dump_dir.md5sums_file, 'wikidata-20211006-md5sums.txt')
        self.assertEqual(dump_dir.sha1sums_file, 'wikidata-20211006-sha1sums.txt')
        # Make sure request_dump_dir was called once with all dump dirs
        self.assertEqual(dump_dirs_to_visit, [])