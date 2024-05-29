import unittest
from datetime import datetime, timedelta
from collections import namedtuple
from WikidataDumpGenerationSmokeTests import DumpListingValidator
from WikidataDumpGenerationSmokeTests.DumpListingReader import DumpDirInfo, DumpInfo, DumpAllInfo
from WikidataDumpGenerationSmokeTests.DumpListingValidator import ValidatorResult

class TestDumpListingValidator(unittest.TestCase):
    def test_ensure_hashsum_files_empty(self):
        dump_listing_validator = DumpListingValidator()
        result = dump_listing_validator._ensure_hashsum_files({})
        self.assertEqual(result.valid, True)
        self.assertEqual(result.errors, [])

    def test_ensure_hashsum_files_success(self):
        dump_dirs = {
            'dsf': DumpDirInfo({'ignored'}, 'foo', 'bar'),
            'fdgk': DumpDirInfo({'ignored'}, 'dfr', 'dfs'),
            'dfs': DumpDirInfo({'ignored'}, '124', 'dd'),
            'emtpy_dump_dir_does_not_need_hash_files': DumpDirInfo({}, None, None),
        }
        dump_listing_validator = DumpListingValidator()
        result = dump_listing_validator._ensure_hashsum_files(dump_dirs)
        self.assertEqual(result.valid, True)
        self.assertEqual(result.errors, [])

    def test_ensure_hashsum_files_single_failure(self):
        dump_dirs = {
            'dsf': DumpDirInfo({'ignored'}, 'foo', 'ddd'),
            'fdgk': DumpDirInfo({'ignored'}, 'dfr', None),
            'dfs': DumpDirInfo({'ignored'}, '124', 'dd'),
        }
        dump_listing_validator = DumpListingValidator()
        result = dump_listing_validator._ensure_hashsum_files(dump_dirs)
        self.assertEqual(result.valid, False)
        self.assertEqual(result.errors, ['Missing sha1sum file in dir "fdgk".'])

    def test_ensure_hashsum_files_multiple_failures(self):
        dump_dirs = {
            'dsf': DumpDirInfo({'ignored'}, None, 'ddd'),
            'fdgk': DumpDirInfo({'ignored'}, 'dfr', None),
            'dfs': DumpDirInfo({'ignored'}, '124', 'dd'),
        }
        dump_listing_validator = DumpListingValidator()
        result = dump_listing_validator._ensure_hashsum_files(dump_dirs)
        self.assertEqual(result.valid, False)
        self.assertEqual(result.errors, [
            'Missing md5sum file in dir "dsf".',
            'Missing sha1sum file in dir "fdgk".',
            ])

    def test_ensure_latest_empty(self):
        dump_listing_validator = DumpListingValidator()
        result = dump_listing_validator._ensure_latest({})
        self.assertEqual(result.valid, True)
        self.assertEqual(result.errors, [])

    def test_ensure_latest_success(self):
        dump_listing_validator = DumpListingValidator()
        result = dump_listing_validator._ensure_latest({
            'a': DumpInfo(222, datetime.now()),
            'b': DumpInfo(222, datetime.now() - timedelta(days = 7)),
            'c': DumpInfo(222, datetime.now() - timedelta(days = 10)),
        })
        self.assertEqual(result.valid, True)
        self.assertEqual(result.errors, [])

    def test_ensure_latest_single_failure(self):
        dump_listing_validator = DumpListingValidator()
        result = dump_listing_validator._ensure_latest({
            'a': DumpInfo(222, datetime.now()),
            'b': DumpInfo(222, datetime.now() - timedelta(days = 14)),
            'c': DumpInfo(222, datetime.now() - timedelta(days = 10)),
        })
        self.assertEqual(result.valid, False)
        self.assertEqual(result.errors, ['Latest dump "b" is too old (14 days).'])

    def test_ensure_latest_multiple_failures(self):
        dump_listing_validator = DumpListingValidator()
        result = dump_listing_validator._ensure_latest({
            'a': DumpInfo(222, datetime.now()),
            'b': DumpInfo(222, datetime.now() - timedelta(days = 14)),
            'to-small': DumpInfo(50, datetime.now()),
            'latest-mediainfo.nt.gz': DumpInfo(222, datetime.now() - timedelta(days = 100)),
            'sdfdsfs': DumpInfo(222, datetime.now())
        })
        self.assertEqual(result.valid, False)
        self.assertEqual(result.errors, [
            'Latest dump "b" is too old (14 days).',
            'Latest dump "to-small" seems empty (probably a broken symlink).',
            'Latest dump "latest-mediainfo.nt.gz" is too old (100 days).',
        ])

    def test_group_dumps_by_type_empty(self):
        dump_listing_validator = DumpListingValidator()
        dumps_by_type = dump_listing_validator._group_dumps_by_type({})
        self.assertEqual(dumps_by_type, {})

    def test_group_dumps_by_type(self):
        dump_listing_validator = DumpListingValidator()

        lexemes_bz2_20211006 = DumpInfo(195288101, datetime.fromisoformat('2021-10-06'))
        lexemes_gz_20211006 = DumpInfo(271807724, datetime.fromisoformat('2021-10-06'))
        truthy_bz2_20211006 = DumpInfo(30708742696, datetime.fromisoformat('2021-10-09'))
        truthy_gz_20211006 = DumpInfo(50187553542, datetime.fromisoformat('2021-10-09'))

        lexemes_bz2_20211013 = DumpInfo(196060822, datetime.fromisoformat('2021-10-13'))
        lexemes_gz_20211013 = DumpInfo(272816734, datetime.fromisoformat('2021-10-13'))
        truthy_bz2_20211013 = DumpInfo(30768656015, datetime.fromisoformat('2021-10-13'))
        truthy_gz_20211013 = DumpInfo(50291842035, datetime.fromisoformat('2021-10-13'))

        dumps_by_type = dump_listing_validator._group_dumps_by_type({
            '20211006/': DumpDirInfo({
                'wikidata-20211006-lexemes.json.bz2': lexemes_bz2_20211006,
                'wikidata-20211006-lexemes.json.gz': lexemes_gz_20211006,
                'wikidata-20211006-truthy-BETA.nt.bz2': truthy_bz2_20211006,
                'wikidata-20211006-truthy-BETA.nt.gz': truthy_gz_20211006,
            }, None, None),
            '20211013/': DumpDirInfo({
                'wikidata-20211013-lexemes.json.bz2': lexemes_bz2_20211013,
                'wikidata-20211013-lexemes.json.gz': lexemes_gz_20211013,
                'wikidata-20211013-truthy-BETA.nt.bz2': truthy_bz2_20211013,
                'wikidata-20211013-truthy-BETA.nt.gz': truthy_gz_20211013,
            }, None, None),
        })
        self.assertEqual(dumps_by_type, {
            'wikidata-lexemes.json.bz2': {
                'wikidata-20211006-lexemes.json.bz2': lexemes_bz2_20211006,
                'wikidata-20211013-lexemes.json.bz2': lexemes_bz2_20211013,
            },
            'wikidata-lexemes.json.gz': {
                'wikidata-20211006-lexemes.json.gz': lexemes_gz_20211006,
                'wikidata-20211013-lexemes.json.gz': lexemes_gz_20211013,
            },
            'wikidata-truthy-BETA.nt.bz2': {
                'wikidata-20211006-truthy-BETA.nt.bz2': truthy_bz2_20211006,
                'wikidata-20211013-truthy-BETA.nt.bz2': truthy_bz2_20211013
            },
            'wikidata-truthy-BETA.nt.gz': {
                'wikidata-20211006-truthy-BETA.nt.gz': truthy_gz_20211006,
                'wikidata-20211013-truthy-BETA.nt.gz': truthy_gz_20211013,
            },
        })

    def test_ensure_dump_size_empty(self):
        dump_listing_validator = DumpListingValidator()
        result = dump_listing_validator._ensure_dump_sizes({})
        self.assertEqual(result.valid, True)
        self.assertEqual(result.errors, [])

    def test_ensure_dump_sizes(self):
        dump_listing_validator = DumpListingValidator()

        lexemes_bz2_20211006 = DumpInfo(195288101, datetime.fromisoformat('2021-10-06'))
        truthy_gz_20211006 = DumpInfo(50187553542, datetime.fromisoformat('2021-10-09'))

        lexemes_bz2_20211013 = DumpInfo(196060822, datetime.fromisoformat('2021-10-13'))
        truthy_gz_20211013 = DumpInfo(50291842035, datetime.fromisoformat('2021-10-13'))

        dumps_by_type = {
            'wikidata-lexemes.json.bz2': {
                'wikidata-20211006-lexemes.json.bz2': lexemes_bz2_20211006,
                'wikidata-20211013-lexemes.json.bz2': lexemes_bz2_20211013,
            },
            'wikidata-truthy-BETA.nt.gz': {
                'wikidata-20211006-truthy-BETA.nt.gz': truthy_gz_20211006,
                'wikidata-20211013-truthy-BETA.nt.gz': truthy_gz_20211013,
            },
        }
        result = dump_listing_validator._ensure_dump_sizes(dumps_by_type)
        self.assertEqual(result.valid, True)
        self.assertEqual(result.errors, [])

    def test_ensure_dump_sizes_single_failure(self):
        dump_listing_validator = DumpListingValidator()

        lexemes_bz2_20211006 = DumpInfo(195288101, datetime.fromisoformat('2021-10-06'))
        truthy_gz_20211006 = DumpInfo(50187553542, datetime.fromisoformat('2021-10-09'))

        lexemes_bz2_20211013 = DumpInfo(195288105, datetime.fromisoformat('2021-10-13'))
        truthy_gz_20211013 = DumpInfo(50291842035, datetime.fromisoformat('2021-10-13'))

        dumps_by_type = {
            'wikidata-lexemes.json.bz2': {
                'wikidata-20211006-lexemes.json.bz2': lexemes_bz2_20211006,
                'wikidata-20211013-lexemes.json.bz2': lexemes_bz2_20211013,
            },
            'wikidata-truthy-BETA.nt.gz': {
                'wikidata-20211006-truthy-BETA.nt.gz': truthy_gz_20211006,
                'wikidata-20211013-truthy-BETA.nt.gz': truthy_gz_20211013,
            },
        }
        result = dump_listing_validator._ensure_dump_sizes(dumps_by_type)
        self.assertEqual(result.valid, False)
        self.assertEqual(
            result.errors, [
                'Dump wikidata-20211013-lexemes.json.bz2 should be at least 195385745 bytes (is 195288105 bytes).',
            ] )

    def test_ensure_dump_sizes_multiple_failures(self):
        dump_listing_validator = DumpListingValidator()

        lexemes_bz2_20211006 = DumpInfo(195288101, datetime.fromisoformat('2021-10-06'))
        truthy_gz_20211006 = DumpInfo(50187553542, datetime.fromisoformat('2021-10-09'))

        lexemes_bz2_20211013 = DumpInfo(195288105, datetime.fromisoformat('2021-10-13'))
        truthy_gz_20211013 = DumpInfo(0, datetime.fromisoformat('2021-10-13'))

        dumps_by_type = {
            'wikidata-lexemes.json.bz2': {
                'wikidata-20211006-lexemes.json.bz2': lexemes_bz2_20211006,
                'wikidata-20211013-lexemes.json.bz2': lexemes_bz2_20211013,
            },
            'wikidata-truthy-BETA.nt.gz': {
                'wikidata-20211006-truthy-BETA.nt.gz': truthy_gz_20211006,
                'wikidata-20211013-truthy-BETA.nt.gz': truthy_gz_20211013,
            },
        }
        result = dump_listing_validator._ensure_dump_sizes(dumps_by_type)
        self.assertEqual(result.valid, False)
        self.assertEqual(
            result.errors, [
                'Dump wikidata-20211013-lexemes.json.bz2 should be at least 195385745 bytes (is 195288105 bytes).',
                'Dump wikidata-20211013-truthy-BETA.nt.gz should be at least 50212647318 bytes (is 0 bytes).',
            ] )

    def test_merge_results_empty(self):
        dump_listing_validator = DumpListingValidator()

        result = dump_listing_validator._merge_results()
        self.assertEqual(result.valid, True)
        self.assertEqual(result.errors, [])

    def test_merge_results_good_single(self):
        dump_listing_validator = DumpListingValidator()

        result = dump_listing_validator._merge_results(ValidatorResult(True, []))
        self.assertEqual(result.valid, True)
        self.assertEqual(result.errors, [])

    def test_merge_results_good_multiple(self):
        dump_listing_validator = DumpListingValidator()

        result = dump_listing_validator._merge_results(ValidatorResult(True, []), ValidatorResult(True, []))
        self.assertEqual(result.valid, True)
        self.assertEqual(result.errors, [])

    def test_merge_results_bad_single(self):
        dump_listing_validator = DumpListingValidator()

        result = dump_listing_validator._merge_results(ValidatorResult(False, ['a']))
        self.assertEqual(result.valid, False)
        self.assertEqual(result.errors, ['a'])

    def test_merge_results_bad_multiple(self):
        dump_listing_validator = DumpListingValidator()

        result = dump_listing_validator._merge_results(ValidatorResult(False, ['a']), ValidatorResult(False, ['b']), ValidatorResult(True, []))
        self.assertEqual(result.valid, False)
        self.assertEqual(result.errors, ['a', 'b'])

    def test_validate_listing_empty(self):
        dump_listing_validator = DumpListingValidator()

        result = dump_listing_validator.validate_listing(DumpAllInfo({}, {}))
        self.assertEqual(result.valid, True)
        self.assertEqual(result.errors, [])

    def test_validate_listing_success(self):
        dump_listing_validator = DumpListingValidator()

        lexemes_bz2_20211006 = DumpInfo(1000, datetime.fromisoformat('2021-10-06'))
        lexemes_bz2_20211007 = DumpInfo(2000, datetime.fromisoformat('2021-10-06'))
        lexemes_bz2_20211008 = DumpInfo(3000, datetime.fromisoformat('2021-10-06'))

        dump_dirs = {
            'dsf': DumpDirInfo({
                'wikidata-20211006-lexemes.json.bz2': lexemes_bz2_20211006
            }, 'foo', 'bar'),
            'fdgk': DumpDirInfo({
                'wikidata-20211007-lexemes.json.bz2': lexemes_bz2_20211007
            }, 'dfr', 'dfs'),
            'dfs': DumpDirInfo({
                'wikidata-20211008-lexemes.json.bz2': lexemes_bz2_20211008
            }, '124', 'dd'),
        }
        latest = {
            'a': DumpInfo(222, datetime.now()),
            'b': DumpInfo(222, datetime.now() - timedelta(days = 7)),
            'c': DumpInfo(222, datetime.now() - timedelta(days = 10)),
        }

        result = dump_listing_validator.validate_listing(DumpAllInfo(latest, dump_dirs))
        self.assertEqual(result.valid, True)
        self.assertEqual(result.errors, [])

    def test_validate_listing_hashsum_file_failure(self):
        dump_listing_validator = DumpListingValidator()

        lexemes_bz2_20211006 = DumpInfo(10000, datetime.fromisoformat('2021-10-06'))
        dump_dirs = {
            'dsf': DumpDirInfo({
                'wikidata-20211006-lexemes.json.bz2': lexemes_bz2_20211006
            }, None, 'bar'),
            'fdgk': DumpDirInfo({
                'wikidata-20211006-lexemes.json.bz2': lexemes_bz2_20211006
            }, 'dfr', 'dfs'),
        }
        result = dump_listing_validator.validate_listing(DumpAllInfo({}, dump_dirs))
        self.assertEqual(result.valid, False)
        self.assertEqual(result.errors, ['Missing md5sum file in dir "dsf".'])

    def test_validate_listing_latest_failure(self):
        dump_listing_validator = DumpListingValidator()

        latest = {
            'a': DumpInfo(222, datetime.now()),
            'b': DumpInfo(222, datetime.now() - timedelta(days = 70)),
            'c': DumpInfo(222, datetime.now() - timedelta(days = 10)),
        }

        result = dump_listing_validator.validate_listing(DumpAllInfo(latest, {}))
        self.assertEqual(result.valid, False)
        self.assertEqual(result.errors, ['Latest dump "b" is too old (70 days).'])

    def test_validate_listing_size_failure(self):
        dump_listing_validator = DumpListingValidator()

        lexemes_bz2_20211006 = DumpInfo(10000, datetime.fromisoformat('2021-10-06'))
        # This is (unexpectedly) much smaller -> failure
        lexemes_bz2_20211007 = DumpInfo(8000, datetime.fromisoformat('2021-10-07'))
        # This is larger again (compared to previous dump only) -> should be fine
        lexemes_bz2_20211008 = DumpInfo(9000, datetime.fromisoformat('2021-10-08'))

        dump_dirs = {
            'dsf': DumpDirInfo({
                'wikidata-20211006-lexemes.json.bz2': lexemes_bz2_20211006
            }, 'foo', 'bar'),
            'fdgk': DumpDirInfo({
                'wikidata-20211007-lexemes.json.bz2': lexemes_bz2_20211007
            }, 'dfr', 'dfs'),
            'dfs': DumpDirInfo({
                'wikidata-20211008-lexemes.json.bz2': lexemes_bz2_20211008
            }, '124', 'dd'),
        }

        result = dump_listing_validator.validate_listing(DumpAllInfo({}, dump_dirs))
        self.assertEqual(result.valid, False)
        self.assertEqual(result.errors, ['Dump wikidata-20211007-lexemes.json.bz2 should be at least 10005 bytes (is 8000 bytes).'])

    def test_validate_listing_multiple_failures(self):
        dump_listing_validator = DumpListingValidator()

        lexemes_bz2_20211006 = DumpInfo(10000, datetime.fromisoformat('2021-10-06'))
        lexemes_bz2_20211007 = DumpInfo(10000, datetime.fromisoformat('2021-10-06'))
        lexemes_bz2_20211008 = DumpInfo(0, datetime.fromisoformat('2021-10-06'))

        dump_dirs = {
            'dsf': DumpDirInfo({
                'wikidata-20211006-lexemes.json.bz2': lexemes_bz2_20211006
            }, 'foo', 'bar'),
            'fdgk': DumpDirInfo({
                'wikidata-20211007-lexemes.json.bz2': lexemes_bz2_20211007
            }, 'dfr', None),
            'dfs': DumpDirInfo({
                'wikidata-20211008-lexemes.json.bz2': lexemes_bz2_20211008
            }, '124', 'dd'),
        }
        latest = {
            'a': DumpInfo(222, datetime.now()),
            'b': DumpInfo(222, datetime.now() - timedelta(days = 70)),
            'c': DumpInfo(222, datetime.now() - timedelta(days = 122)),
        }

        result = dump_listing_validator.validate_listing(DumpAllInfo(latest, dump_dirs))
        self.assertEqual(result.valid, False)
        self.assertEqual(result.errors, [
            'Missing sha1sum file in dir "fdgk".',
            'Latest dump "b" is too old (70 days).',
            'Latest dump "c" is too old (122 days).',
            'Dump wikidata-20211007-lexemes.json.bz2 should be at least 10005 bytes (is 10000 bytes).',
            'Dump wikidata-20211008-lexemes.json.bz2 should be at least 10005 bytes (is 0 bytes).',
        ])
