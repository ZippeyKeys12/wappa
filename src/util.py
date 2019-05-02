from sty import fg

from src.gen.Wappa import Token

severity_levels = {
    "FATAL",
    "ERROR",
    "WARNING",
    "INFO"
}


def Exception(severity: str, arg: str, tok: Token):
    if severity not in severity_levels:
        raise ValueError(
            'severity_level must be in: {}'.format(severity_levels))

    print("{}[{}] - {} at line {.line}{}".format({
        "FATAL": fg.white,
        "ERROR": fg.li_red,
        "WARNING": fg.li_yellow,
        "INFO": fg.li_green,
    }[severity], severity, arg, tok, fg.rs))

    # if severity in ["FATAL", "ERROR"]:
    #     exit(1)
