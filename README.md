## wikidata-dump-generation-smoke-tests
Smoke tests for Wikidata and Wikimedia Commons Wikibase entity dump generation.

These tests ensure that all `latest-*` dumps are recent, the dump sizes look sane and hash sum files are correctly generated.

This reads from either https://dumps.wikimedia.org/wikidatawiki/entities/ (wikidata) or https://dumps.wikimedia.org/commonswiki/entities/ (commons).

### Usage
See `wikidata-dump-generation-smoke-tests --help`.