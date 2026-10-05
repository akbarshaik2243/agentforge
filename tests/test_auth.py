import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agentforge import AuthError, TokenStore, require_scope


def _store():
    return TokenStore("tok-alice:alice:tools.read,tools.write;tok-bob:bob:tools.read")


def test_valid_token_authenticates():
    user = _store().authenticate("tok-alice")
    assert user.id == "alice"
    assert "tools.write" in user.scopes


def test_unknown_token_rejected():
    try:
        _store().authenticate("tok-eve")
    except AuthError:
        return
    raise AssertionError("unknown token was accepted")


def test_missing_token_rejected():
    try:
        _store().authenticate(None)
    except AuthError:
        return
    raise AssertionError("missing token was accepted")


def test_scope_granted():
    require_scope(_store().authenticate("tok-alice"), "tools.write")


def test_scope_denied():
    try:
        require_scope(_store().authenticate("tok-bob"), "tools.write")
    except AuthError:
        return
    raise AssertionError("missing scope was granted")
