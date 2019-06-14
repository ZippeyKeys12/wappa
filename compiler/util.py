from __future__ import annotations

from functools import singledispatch, update_wrapper
from typing import List, Tuple

from sty import fg

from gen.Wappa import Token

severity_levels = {
    "FATAL",
    "ERROR",
    "WARNING",
    "INFO"
}

EXCEPTION_LIST: List[Tuple[str, str, str, Token, str]] = []


def WappaException(severity: str, arg: str, tok: Token):
    if severity not in severity_levels:
        raise ValueError(
            'severity_level must be in: {}'.format(severity_levels))

    EXCEPTION_LIST.append(({
        "FATAL": fg.white,
        "ERROR": fg.li_red,
        "WARNING": fg.li_yellow,
        "INFO": fg.li_green,
    }[severity], severity, arg, tok.line, fg.rs))

    print(EXCEPTION_LIST[-1])

    # if severity in ["FATAL", "ERROR"]:
    #     exit(1)


def methoddispatch(func):
    dispatcher = singledispatch(func)

    def wrapper(*args, **kw):
        return dispatcher.dispatch(args[1].__class__)(*args, **kw)

    wrapper.register = dispatcher.register
    update_wrapper(wrapper, func)
    return wrapper
