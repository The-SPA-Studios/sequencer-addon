# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2023, The SPA Studios. All rights reserved.

import sys

import mypy.api


SOURCE_FOLDER = "spa_sequencer"


def main():
    """Run static analysis and return mypy's exit code."""
    stdout, stderr, rc = mypy.api.run([SOURCE_FOLDER])

    if stdout:
        print(f"Type checking report:\n{stdout}")

    if stderr:
        print(f"Error report:\n{stderr}")

    print(f"Mypy exit status: {rc}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
