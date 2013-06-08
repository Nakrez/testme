import sys

stdin = sys.stdin.read()
if stdin != "":
    print stdin,
else:
    sys.exit(1)
