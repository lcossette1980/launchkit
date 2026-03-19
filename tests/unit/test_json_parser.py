"""Tests for the JSON extraction and validation module."""

from gtm.llm.json_parser import extract_json, parse_and_validate, safe_parse
from gtm.schemas.analysis import ScoresSchema


class TestExtractJson:
    def test_raw_json(self):
        assert extract_json('{"a": 1}') == {"a": 1}

    def test_markdown_json_block(self):
        text = 'Here is the result:\n```json\n{"key": "val"}\n```\nDone.'
        assert extract_json(text) == {"key": "val"}

    def test_plain_code_block(self):
        text = '```\n{"x": 2}\n```'
        assert extract_json(text) == {"x": 2}

    def test_regex_fallback(self):
        text = 'Some prose before {"nested": true} and after.'
        assert extract_json(text) == {"nested": True}

    def test_empty_string(self):
        assert extract_json("") == {}

    def test_no_json_found(self):
        assert extract_json("just plain text no braces") == {}

    def test_whitespace_only(self):
        assert extract_json("   \n\t  ") == {}

    def test_nested_json(self):
        text = '{"outer": {"inner": [1, 2, 3]}}'
        result = extract_json(text)
        assert result["outer"]["inner"] == [1, 2, 3]


class TestParseAndValidate:
    def test_valid_scores(self):
        text = '{"clarity": 80, "audience_fit": 70, "conversion": 60, "seo": 50, "ux": 90}'
        result = parse_and_validate(text, ScoresSchema)
        assert result is not None
        assert result.clarity == 80
        assert result.ux == 90

    def test_invalid_returns_none(self):
        # Score > 100 should fail validation
        text = '{"clarity": 200}'
        result = parse_and_validate(text, ScoresSchema)
        assert result is None

    def test_empty_text(self):
        assert parse_and_validate("", ScoresSchema) is None


class TestSafeParse:
    def test_fallback_to_defaults(self):
        result = safe_parse("not json at all", ScoresSchema)
        assert result.clarity == 0
        assert result.seo == 0

    def test_valid_input(self):
        result = safe_parse('{"clarity": 42}', ScoresSchema)
        assert result.clarity == 42
