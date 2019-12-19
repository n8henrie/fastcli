"""test_fastcli.py :: Tests for `fastcli` module."""

import urllib.error
import urllib.request

from fastcli import fastcli


def test_find_from() -> None:
    """Test the hacky `_find_from` function

    Should return the first portion of `text` between `start` and `until`
    """
    assert (
        fastcli._find_from(
            text='<script src="/12345.js"', start='<script src="', until='"'
        )
        == "/12345.js"
    )


def internet_is_on() -> bool:
    """Utility function to try to verify an internet connection exists"""
    headers = {"User-Agent": "fastcli"}
    req = urllib.request.Request("https://n8henrie.com", headers=headers)

    try:
        with urllib.request.urlopen(req) as r:
            resp = dict(r.getheaders())
    except urllib.error.URLError:
        resp = {}

    if resp.get("Date"):
        return True
    else:
        return False


def test_fastcli() -> None:
    """If an internet connect exists, it should have a measurable speed > 0"""
    if internet_is_on():
        assert fastcli.run(timeout=1) > 0
