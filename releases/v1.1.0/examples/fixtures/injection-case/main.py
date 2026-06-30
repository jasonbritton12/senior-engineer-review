import subprocess
import sys


def run(cmd):
    # Planted (Critical): shell=True with unsanitized input enables command injection.
    return subprocess.run(cmd, shell=True)


if __name__ == "__main__":
    run(sys.argv[1])
