# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2023, The SPA Studios. All rights reserved.


def test_load_addon():
    """Ensure addon loads correctly."""
    import addon_utils

    assert addon_utils.check("spa_sequencer")[1]
