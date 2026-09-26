from __future__ import annotations

from contextvars import ContextVar, Token

_current_actor: ContextVar[str] = ContextVar("current_actor", default="")


def set_current_actor(actor: str) -> Token:
    return _current_actor.set(actor)


def get_current_actor() -> str:
    return _current_actor.get()


def reset_current_actor(token: Token) -> None:
    _current_actor.reset(token)
