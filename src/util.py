def Exception(arg, tok):
    print("{} at {}".format(arg, "Line {0.line}".format(tok)))
    exit()
