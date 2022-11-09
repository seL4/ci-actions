# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

from platforms import platforms, gh_output
import sys

if __name__ == '__main__':
    if len(sys.argv) == 2:
        plat = platforms.get(sys.argv[1].upper())
        if plat:
            gh_output(f"march={plat.march}")
            sys.exit(0)
        else:
            print(f"Unknown platform {sys.argv[1]}")
            sys.exit(1)

    sys.exit(1)
