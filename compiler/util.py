from __future__ import annotations

from functools import singledispatch, update_wrapper
from typing import List, Tuple

from gen.Wappa import Token

severity_levels = {
    "FATAL",
    "ERROR",
    "WARNING",
    "INFO"
}

EXCEPTION_LIST: List[Tuple[str, str, str, Token]] = []


def WappaException(severity: str, arg: str, tok: Token):
    if severity not in severity_levels:
        raise ValueError(
            'severity_level must be in: {}'.format(severity_levels))

    # {
    #     "FATAL": fg.white,
    #     "ERROR": fg.li_red,
    #     "WARNING": fg.li_yellow,
    #     "INFO": fg.li_green,
    # }[severity]

    EXCEPTION_LIST.append((severity, arg, tok.line))

    # print(EXCEPTION_LIST[-1])

    # if severity in ["FATAL", "ERROR"]:
    #     exit(1)


def methoddispatch(func):
    dispatcher = singledispatch(func)

    def wrapper(*args, **kw):
        return dispatcher.dispatch(args[1].__class__)(*args, **kw)

    wrapper.register = dispatcher.register
    update_wrapper(wrapper, func)
    return wrapper
