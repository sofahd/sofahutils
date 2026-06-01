"""
Tests for SofahLogger's request shaping -- specifically that an optional pot-owned
session id is forwarded to the /log endpoint (and omitted when not given).
"""
import types

import sofahutils.logger as logger_module
from sofahutils import SofahLogger


class _Resp:
    def __init__(self, text="OK", status=200):
        self.text = text
        self.status_code = status

    def json(self):
        return {}


def _patch_requests(monkeypatch, posts):
    fake = types.SimpleNamespace(
        get=lambda url: _Resp("OK", 200),                          # health check
        post=lambda url, data=None: posts.append(data) or _Resp("OK", 200),
    )
    monkeypatch.setattr(logger_module, "requests", fake)


def test_log_forwards_pot_owned_session(monkeypatch):
    posts = []
    _patch_requests(monkeypatch, posts)
    log = SofahLogger(url="http://log_api:50005")
    log.log(event_id="ssh.honeypot.login", content={"user": "root"}, ip="1.2.3.4", port=22, session="sess-1")
    assert posts[-1]["session"] == "sess-1"


def test_log_omits_session_when_not_given(monkeypatch):
    posts = []
    _patch_requests(monkeypatch, posts)
    log = SofahLogger(url="http://log_api:50005")
    log.log(event_id="ssh.honeypot.login", content={"user": "root"}, ip="1.2.3.4", port=22)
    assert "session" not in posts[-1]
