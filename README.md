## wikidata-dump-generation-smoke-tests
Smoke tests for Wikidata and Wikimedia Commons Wikibase entity dump generation.

These tests ensure that all `latest-*` dumps are recent, the dump sizes look sane and hash sum files are correctly generated.

This reads from either https://dumps.wikimedia.org/wikidatawiki/entities/ (wikidata) or https://dumps.wikimedia.org/commonswiki/entities/ (commons).

This is run as cron job on `stat1005.eqiad.wmnet` ([details](https://gist.github.com/mariushoch/203e7b65b1d6059cdaaf6e824d9eaccf)).

### Usage
See `wikidata-dump-generation-smoke-tests --help`.

### Tests
Use `python -m unittest` to run the python unit tests and `bats wikidata-dump-generation-smoke-tests.bats` to run the integration tests.
