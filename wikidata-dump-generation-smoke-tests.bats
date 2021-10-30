#!/usr/bin/env bats

@test "wikidata-dump-generation-smoke-tests: help" {
        run "$BATS_TEST_DIRNAME/wikidata-dump-generation-smoke-tests" --help
        [ "$status" -eq 0 ]
        [[ "$output" =~ "usage: wikidata-dump-generation-smoke-tests" ]]
}
@test "wikidata-dump-generation-smoke-tests: missing arg" {
        run "$BATS_TEST_DIRNAME/wikidata-dump-generation-smoke-tests"
        [ "$status" -ne 0 ]
        [[ "$output" =~ one\ of.*required ]]
}
@test "wikidata-dump-generation-smoke-tests --test-wikidata" {
        run "$BATS_TEST_DIRNAME/wikidata-dump-generation-smoke-tests" --test-wikidata
        [ "$status" -eq 0 ]
        [ "$output" == "" ]
}
@test "wikidata-dump-generation-smoke-tests --test-commons" {
        run "$BATS_TEST_DIRNAME/wikidata-dump-generation-smoke-tests" --test-commons
        [ "$status" -eq 0 ]
        [ "$output" == "" ]
}
@test "wikidata-dump-generation-smoke-tests --test-wikidata: failure" {
        run "$BATS_TEST_DIRNAME/wikidata-dump-generation-smoke-tests" --test-wikidata --max-last-age 1
        [ "$status" -eq 1 ]
echo "$output"
	[[ "$output" =~ Latest\ dump\ \"latest-.*\"\ is\ too\ old\ \([0-9]+\ days\)\. ]]
}
@test "wikidata-dump-generation-smoke-tests --test-commons: failure" {
        run "$BATS_TEST_DIRNAME/wikidata-dump-generation-smoke-tests" --test-commons --expected-size-multiplicator 1.5
        [ "$status" -eq 1 ]
echo "$output"
	[[ "$output" =~ Dump\ commons-.*should\ be\ at\ least\ [0-9]+\ bytes\ \(is\ [0-9]+\ bytes\)\. ]]
}
