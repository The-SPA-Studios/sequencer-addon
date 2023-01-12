# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2023, The SPA Studios. All rights reserved.

import pytest

import bpy

from spa_sequencer.shot.naming import ShotNaming, ShotPrefix
from spa_sequencer.shot.core import duplicate_scene


shot_naming = ShotNaming()
# Define shot prefixes for unit testing
shot_naming.prefixes = [ShotPrefix.SHOT.value, ShotPrefix.PREVIZ.value]


def test_get_default_shot_name():
    assert shot_naming.default_shot_name() == "SH0010"


def test_get_next_shot_name_from_default():
    name = shot_naming.default_shot_name()
    assert shot_naming.next_shot_name_from_name(name) == "SH0020"


def test_get_next_shot_name_custom_increment():
    name = shot_naming.default_shot_name()
    assert shot_naming.next_shot_name_from_name(name, 5) == "SH0015"


def test_get_next_shot_name_snap_to_spacing():
    assert shot_naming.next_shot_name_from_name("SH0015") == "SH0020"


def test_get_next_shot_name_overflow():
    shot_max = shot_naming.build_shot_name(shot_naming.number_max)
    with pytest.raises(ValueError):
        assert shot_naming.next_shot_name_from_name(shot_max)


def test_build_shot_name_with_prefix():
    # Buils shot name with a valid prefix.
    shot_name = shot_naming.build_shot_name(1, ShotPrefix.PREVIZ.value)
    assert shot_name == f"{ShotPrefix.PREVIZ.value}0001"
    # Extract shot data and ensure they match original shot name.
    shot_data = shot_naming.shot_data_from_name(shot_name, strict=True)
    assert shot_data.prefix == ShotPrefix.PREVIZ.value
    assert shot_data.number == 1


def test_build_shot_name_with_invalid_prefix():
    # Build shot name with invalid prefix.
    shot_name = "INV0012"
    shot_data = shot_naming.shot_data_from_name(shot_name, strict=False)
    # Shot prefix has been discarded.
    assert shot_data.prefix == shot_naming.prefix_default
    # Shot number has been preserved
    assert shot_data.number == 12

    # Using string naming should raise an error.
    with pytest.raises(ValueError):
        shot_naming.shot_data_from_name(shot_name, strict=True)


def test_build_shot_name_with_take():
    take_A = shot_naming.build_shot_name(10, take="A")
    assert take_A == "SH0010A"
    assert shot_naming.next_take_name(take_A) == "SH0010B"


def test_build_shot_name_with_take_overflow():
    take_F = shot_naming.build_shot_name(10, take="F")
    assert take_F == "SH0010F"
    with pytest.raises(ValueError):
        shot_naming.next_take_name(take_F)


def test_build_shot_name_with_invalid_take_value():
    with pytest.raises(ValueError):
        shot_naming.build_shot_name(10, take="9")


def test_get_new_shot_name_alt_naming():
    # Create a local naming convention
    naming = ShotNaming()
    naming.prefixes = ["SHOT"]
    naming.separator = "_"
    naming.number_default = 0
    naming.number_digits = 3
    naming.number_spacing = 1

    # Ensure first shot name is correct and respect alternative naming
    assert naming.default_shot_name() == "SHOT_000"


def test_get_new_shot_name_no_shot_scene():
    # Rename scene to something that is not a shot
    bpy.context.scene.name = "TEST"

    new_shot_name = shot_naming.next_shot_name_from_scenes()
    # Ensure first shot name is correct
    assert new_shot_name == shot_naming.default_shot_name() == "SH0010"


def test_get_new_shot_name_increment_shot_number():
    bpy.context.scene.name = "SH0010"
    new_shot_name = shot_naming.next_shot_name_from_scenes()
    # Ensure next shot name is correct
    assert new_shot_name == "SH0020"


def test_get_new_shot_name_increment_highest_shot_number():
    bpy.context.scene.name = "SH0010"

    # Create a few shots
    ref_scene = bpy.context.scene
    duplicate_scene(bpy.context, ref_scene, "SH0015")
    duplicate_scene(bpy.context, ref_scene, "SH0019")

    new_shot_name = shot_naming.next_shot_name_from_scenes()
    # Ensure that the new name snaps to spacing.
    assert new_shot_name == "SH0020"
    duplicate_scene(bpy.context, ref_scene, "SH0020")

    new_shot_name = shot_naming.next_shot_name_from_scenes()
    # Next shot should add spacing.
    assert new_shot_name == "SH0030"
