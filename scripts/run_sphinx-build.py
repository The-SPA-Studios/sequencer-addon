# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2023, The SPA Studios. All rights reserved.

import os
import sys

from sphinx.cmd import build


CONFIG_FOLDER = "apidoc"
BUILD_FOLDER = os.path.join(CONFIG_FOLDER, "generated", "build")


def main():
    """Run sphinx-build to generate a HTML version of addon's API documentation."""

    # Build sphinx doc
    return build.make_main(["M", "html", CONFIG_FOLDER, BUILD_FOLDER])


if __name__ == "__main__":
    sys.exit(main())
