from datetime import datetime, timedelta
import re
from typing import NamedTuple

class ValidatorResult(NamedTuple):
    valid: bool
    errors: list

class DumpListingValidator():
    max_latest_age = None
    expected_size_multiplicator = None

    def __init__(self, max_latest_age = 10, expected_size_multiplicator = 1.0005):
        self.max_latest_age = max_latest_age + 1
        self.expected_size_multiplicator = expected_size_multiplicator

    def _ensure_hashsum_files(self, dump_dirs) -> ValidatorResult:
        """
        Make sure all dump directories have both md5 and sha1 hash sum files.
        """
        valid = True
        errors = []

        for dump_dir_name, dump_dir in dump_dirs.items():
            if not dump_dir.dumps:
                # No dumps, no need for hashes
                continue
            if not dump_dir.md5sums_file:
                valid = False
                errors.append('Missing md5sum file in dir "' + dump_dir_name + '".')
            if not dump_dir.sha1sums_file:
                valid = False
                errors.append('Missing sha1sum file in dir "' + dump_dir_name + '".')

        return ValidatorResult(valid, errors)

    def _ensure_latest(self, latest) -> ValidatorResult:
        """
        Make sure all "latest" dumps are recent enough (at most self.max_latest_age days).
        """
        now = datetime.now()
        valid = True
        errors = []

        for latest_name, latest_date in latest.items():
            age = now - latest_date
            # Older than expected
            if age > timedelta(days = self.max_latest_age):
                valid = False
                errors.append('Latest dump "' + latest_name + '" is too old (' + str(age.days) + ' days).')

        return ValidatorResult(valid, errors)

    def _ensure_dump_sizes(self, dumps_by_type) -> ValidatorResult:
        """
        Make sure all dumps are at least self.expected_size_multiplicator time as large as
        the previous dump of the same type.
        """
        valid = True
        errors = []

        for dump_type, dumps in dumps_by_type.items():
            last_size = 0
            for dump_name, dump in dumps.items():
                expected_size = int(last_size * self.expected_size_multiplicator)
                if dump.size < expected_size:
                    valid = False
                    errors.append(
                        'Dump ' + dump_name + ' should be at least ' + str(expected_size) + ' bytes (is ' + str(dump.size) + ' bytes).'
                    )
                last_size = dump.size

        return ValidatorResult(valid, errors)

    def _group_dumps_by_type(self, dump_dirs):
        dumps_by_type = {}

        for dump_dir_name, dump_dir in dump_dirs.items():
            for dump_name, dump_info in dump_dir.dumps.items():
                canonical_re = re.search(r"(commons|wikidata)-\d+-(.*?\.(gz|bz2))", dump_name)

                if not canonical_re:
                    raise Exception('Cannot normalize dump name "' + dump_name + '".')

                canonical_name = canonical_re.group(1) + '-' + canonical_re.group(2)
                if not canonical_name in dumps_by_type:
                    dumps_by_type[canonical_name] = {}
                dumps_by_type[canonical_name][dump_name] = dump_info

        return dumps_by_type

    def _merge_results(self, *results) -> ValidatorResult:
        valid = True
        errors = []

        for result in results:
            valid = valid and result.valid
            errors += result.errors

        return ValidatorResult(valid, errors)

    def validate_listing(self, dump_all_info) -> ValidatorResult:
        """
        Makes sure the given DumpAllInfo is valid.

        Returns a named tumple containing a bool indicating validity (valid) and a list
        of errors (errors).
        """
        result_hashsum_files = self._ensure_hashsum_files(dump_all_info.dump_dirs)
        result_latest = self._ensure_latest(dump_all_info.latest)
        result_dump_sizes = self._ensure_dump_sizes(self._group_dumps_by_type(dump_all_info.dump_dirs))

        return self._merge_results(result_hashsum_files, result_latest, result_dump_sizes)
