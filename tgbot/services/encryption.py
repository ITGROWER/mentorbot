from __future__ import annotations

from cryptography.fernet import Fernet, InvalidToken

_fernet: Fernet | None = None
_enabled = False


def setup(key: str, *, enabled: bool = True) -> None:
    global _fernet, _enabled
    _enabled = enabled
    if enabled:
        _fernet = Fernet(key.encode())
    else:
        _fernet = None


def encrypt(text: str) -> str:
    if not _enabled or _fernet is None:
        return text
    return _fernet.encrypt(text.encode()).decode()


def decrypt(token: str) -> str:
    if not _enabled or _fernet is None:
        return token
    try:
        return _fernet.decrypt(token.encode()).decode()
    except InvalidToken:
        return token
