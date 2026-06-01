"""
Tests for the helpers promoted into sofahutils from the per-module utils copies.
These pin the behaviour so the consolidation is regression-guarded.
"""
import json
import time
from configparser import ConfigParser

import pytest

import sofahutils
from sofahutils import (
    load_config,
    validate_path_and_extension,
    load_json_file_to_dict,
    repair_folder_path,
    validate_config,
    load_var_from_config_and_validate,
    save_as_json,
    format_unix_timestamp_to_html,
    get_timestamp_now,
    get_random_realistic_time,
    save_list_to_file,
    remove_multiple_substrings_from_string,
    ip_to_digit,
    clean_ip_dict,
    get_own_ip,
    PathIsNoFileException,
    WrongFileTypeException,
    InvalidConfigException,
)


def test_public_surface_reexported():
    # the consolidated names must all be importable straight from the package
    for name in ("load_config", "save_as_json", "get_own_ip",
                 "PathIsNoFileException", "InvalidConfigException"):
        assert hasattr(sofahutils, name)


def test_validate_path_and_extension(tmp_path):
    f = tmp_path / "x.ini"
    f.write_text("[S]\nk = v\n")
    validate_path_and_extension(str(f), ".ini")          # ok, no raise
    validate_path_and_extension(str(f), "ini")           # extension w/o dot also ok
    with pytest.raises(WrongFileTypeException):
        validate_path_and_extension(str(f), ".json")
    with pytest.raises(PathIsNoFileException):
        validate_path_and_extension(str(tmp_path / "nope.ini"), ".ini")


def test_load_config_and_var(tmp_path):
    f = tmp_path / "c.ini"
    f.write_text("[Masscan]\nrate = 1000\n")
    cfg = load_config(str(f))
    assert isinstance(cfg, ConfigParser)
    assert load_var_from_config_and_validate(cfg, "Masscan", "rate") == "1000"
    with pytest.raises(InvalidConfigException):
        validate_config(cfg, "Masscan", "missing")
    with pytest.raises(InvalidConfigException):
        load_var_from_config_and_validate(cfg, "Masscan", "missing")


def test_json_roundtrip(tmp_path):
    f = tmp_path / "d.json"
    save_as_json(str(f), {"a": 1, "b": [2, 3]})
    assert load_json_file_to_dict(str(f)) == {"a": 1, "b": [2, 3]}
    # append + newline mode produces JSON-lines
    save_as_json(str(f), {"x": 1}, mode="w", newline=True)
    save_as_json(str(f), {"x": 2}, mode="a", newline=True)
    lines = [json.loads(l) for l in f.read_text().splitlines()]
    assert lines == [{"x": 1}, {"x": 2}]


def test_load_json_rejects_non_json(tmp_path):
    f = tmp_path / "d.txt"
    f.write_text("{}")
    with pytest.raises(WrongFileTypeException):
        load_json_file_to_dict(str(f))


def test_timestamp_formatting():
    # 1674032784 -> Tue, 18 Jan 2023 ... GMT (format, not tz, is what we assert)
    s = format_unix_timestamp_to_html(1674032784)
    assert s.endswith(" GMT") and "," in s
    assert get_timestamp_now().endswith(" GMT")
    assert get_random_realistic_time().endswith(" GMT")


def test_string_and_path_helpers():
    assert remove_multiple_substrings_from_string("a/b/c..d", ["/", ".."]) == "abcd"
    assert repair_folder_path("/x/y") == "/x/y/"
    assert repair_folder_path("/x/y/") == "/x/y/"
    assert ip_to_digit("10.0.0.7") == 7
    assert ip_to_digit("nope") == -1


def test_save_list_to_file(tmp_path):
    f = tmp_path / "l.txt"
    save_list_to_file(["one", "two"], str(f))
    assert f.read_text() == "one\ntwo\n"


def test_clean_ip_dict_drops_stale_entries():
    now = round(time.time())
    d = {
        "fresh": {"port": "22", "time": now},
        "stale": {"port": "23", "time": now - 90000},  # > 24h
    }
    cleaned = clean_ip_dict(d)
    assert "fresh" in cleaned and "stale" not in cleaned


def test_get_own_ip_no_network_returns_loopback():
    # empty api list -> loop never runs -> default, no network touched
    assert get_own_ip([], logger=None) == "127.0.0.1"
