# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2023, The SPA Studios. All rights reserved.

import bpy

from pytest import fixture

from spa_sequencer.sync.core import remap_frame_value, get_sync_settings

from utils import create_shot_scene


@fixture
def basic_synced_setup() -> tuple[bpy.types.Scene, bpy.types.SceneSequence]:
    """
    Generate a basic setup with an edit scene and 1 shot scene of default length (250f).
    It also enables the sync system.
    Returns the edit scene and the shot strip.
    """
    sync_settings = get_sync_settings()

    # Use default scene as edit scene and create the sequence editor
    edit_scene = bpy.context.scene
    edit_scene.name = "EDIT"
    edit_scene.sequence_editor_create()

    shot_strip = create_shot_scene(edit_scene, 1, 1)

    # Setup and enable sync system
    sync_settings.master_scene = edit_scene
    sync_settings.enabled = True

    return edit_scene, shot_strip


@fixture
def complex_synced_setup(
    basic_synced_setup,
) -> tuple[bpy.types.Scene, list[bpy.types.SceneSequence]]:
    """
    Generate a complex setup with an edit scene and 4 overlapping shots on
    different channels with a scene length of (250f).
    Returns the edit scene and the 4 shot strips.
    """
    edit_scene, shot_strip = basic_synced_setup
    shot_strip_1 = shot_strip
    shot_strip_2 = create_shot_scene(edit_scene, 2, shot_strip.frame_final_start)
    shot_strip_3 = create_shot_scene(edit_scene, 3, shot_strip.frame_final_start)
    shot_strip_4 = create_shot_scene(edit_scene, 4, shot_strip.frame_final_start)

    return (edit_scene, [shot_strip_1, shot_strip_2, shot_strip_3, shot_strip_4])


def test_change_edit_time(basic_synced_setup):
    edit_scene, shot_strip = basic_synced_setup

    # Shorten the strip length
    shot_strip.frame_final_duration = 10

    # Change edit scene's frame within shot's boundaries
    edit_frame = 4
    edit_scene.frame_set(edit_frame)

    # Shot scene's current frame should have changed
    shot_frame = remap_frame_value(edit_frame, shot_strip)
    assert shot_strip.scene.frame_current == shot_frame

    # Change edit scene's frame outside shot's boundaries
    edit_frame = 20
    edit_scene.frame_set(edit_frame)
    # Frame should still be equal to previous value
    assert shot_strip.scene.frame_current == shot_frame


def test_disable_sync(basic_synced_setup):
    edit_scene, shot_strip = basic_synced_setup
    sync_settings = get_sync_settings()

    # Disable the synchronization system
    sync_settings.enabled = False

    # Change edit scene's frame within shot's boundaries
    shot_frame = shot_strip.scene.frame_current
    edit_scene.frame_set(4)

    # Shot frame should not have changed
    assert shot_frame == shot_strip.scene.frame_current


def test_change_master_scene(basic_synced_setup):
    edit_scene, shot_strip = basic_synced_setup
    sync_settings = get_sync_settings()

    # Unset master scene
    sync_settings.master_scene = None

    # Change edit scene's frame within shot's boundaries
    shot_frame = shot_strip.scene.frame_current
    edit_scene.frame_set(4)

    # Shot frame should not have changed
    assert shot_frame == shot_strip.scene.frame_current


def test_window_scene_sync(basic_synced_setup):
    edit_scene, shot_strip_1 = basic_synced_setup

    # Create a 2nd shot after the first one
    create_shot_scene(edit_scene, 1, shot_strip_1.frame_final_end)

    # Start the tests from a neutral scene
    bpy.context.window.scene = edit_scene
    edit_scene.frame_set(0)

    # Moving the edit frame to the start of each strip should
    # update window's scene accordingly.
    for strip in edit_scene.sequence_editor.sequences:
        edit_scene.frame_set(strip.frame_final_start)
        assert bpy.context.window.scene == strip.scene


def test_keep_gp_toolsettings(basic_synced_setup):
    edit_scene, shot_strip_1 = basic_synced_setup
    sync_settings = get_sync_settings()

    sync_settings.keep_gpencil_tool_settings = True

    # Shot 1
    # Create GP object and change tool settings's brush type
    bpy.context.window.scene = shot_strip_1.scene
    bpy.ops.object.gpencil_add(type="MONKEY")
    gpencil_shot_1 = bpy.context.active_object
    gp_settings_1 = shot_strip_1.scene.tool_settings.gpencil_paint
    gp_settings_1.brush = bpy.data.brushes["Pencil"]

    # Shot 2
    # Create a GP object and assign the same materials as the first one
    shot_strip_2 = create_shot_scene(edit_scene, 1, shot_strip_1.frame_final_end)
    bpy.context.window.scene = shot_strip_2.scene
    bpy.ops.object.gpencil_add(type="MONKEY")
    gpencil_shot_2 = bpy.context.active_object
    for idx, material in enumerate(gpencil_shot_1.data.materials):
        gpencil_shot_2.material_slots[idx].material = material
    # Select a different brush type than in Shot 1
    gp_settings_2 = shot_strip_2.scene.tool_settings.gpencil_paint
    gp_settings_2.brush = bpy.data.brushes["Pen"]

    # Shot 3
    # Empty scene
    shot_strip_3 = create_shot_scene(edit_scene, 1, shot_strip_2.frame_final_end)
    gp_settings_3 = shot_strip_3.scene.tool_settings.gpencil_paint

    # Start the tests from a neutral scene
    bpy.context.window.scene = edit_scene
    edit_scene.frame_set(0)

    # Go to Shot 1 and change the active object's material
    edit_scene.frame_set(shot_strip_1.frame_final_start)
    gpencil_shot_1.active_material_index = 2

    # Go to Shot2
    edit_scene.frame_set(shot_strip_2.frame_final_start)

    # Go to Shot3
    edit_scene.frame_set(shot_strip_3.frame_final_start)

    # Check that grease pencil settings are identical for Shot 1 and 2
    assert gp_settings_2.brush == gp_settings_1.brush
    assert gpencil_shot_2.active_material == gpencil_shot_1.active_material
    # Check that a Shot without any GP does not break the system
    assert gp_settings_3 is None


def test_keep_gp_toolsettings_interaction_mode(basic_synced_setup):
    edit_scene, shot_strip_1 = basic_synced_setup
    sync_settings = get_sync_settings()

    sync_settings.keep_gpencil_tool_settings = True

    interaction_mode = "PAINT_GPENCIL"
    # Shot 1
    # Create GP object and change interaction mode
    bpy.context.window.scene = shot_strip_1.scene
    bpy.ops.object.gpencil_add(type="MONKEY")
    gpencil_shot_1 = bpy.context.active_object
    # Go to paint mode
    bpy.ops.object.mode_set(mode=interaction_mode)

    # Shot 2
    # Empty scene
    shot_strip_2 = create_shot_scene(edit_scene, 1, shot_strip_1.frame_final_end)

    # Shot 3
    # Scene with a single GP object
    shot_strip_3 = create_shot_scene(edit_scene, 1, shot_strip_2.frame_final_end)
    bpy.context.window.scene = shot_strip_3.scene
    bpy.ops.object.gpencil_add(type="MONKEY")
    gpencil_shot_3 = bpy.context.active_object

    # Start the tests from a neutral scene
    bpy.context.window.scene = edit_scene
    edit_scene.frame_set(0)

    # Go to Shot 1: active GP object in paint mode
    edit_scene.frame_set(shot_strip_1.frame_final_start)
    # Go to Shot 2: no active object
    edit_scene.frame_set(shot_strip_2.frame_final_start)
    # Go to Shot 3: active GP object initially in object mode
    edit_scene.frame_set(shot_strip_3.frame_final_start)
    # Ensure GP mode was applied to the one in Shot 3, despite Shot 2 being empty
    assert gpencil_shot_1.mode == gpencil_shot_3.mode == interaction_mode


def test_bidirectional_within_shot_range(basic_synced_setup):
    edit_scene, shot_strip_1 = basic_synced_setup

    edit_scene.frame_set(shot_strip_1.frame_final_start)
    assert bpy.context.window.scene == shot_strip_1.scene
    offset = 1
    shot_strip_1.scene.frame_set(shot_strip_1.scene.frame_current + offset)
    assert edit_scene.frame_current == shot_strip_1.frame_final_start + offset


def test_bidirectional_outside_shot_range(basic_synced_setup):
    edit_scene, shot_strip_1 = basic_synced_setup
    edit_scene.frame_set(shot_strip_1.frame_final_start)

    # Go outside scene's range
    shot_strip_1.scene.frame_set(shot_strip_1.scene.frame_end + 10)
    # Master time should not have been updated
    assert edit_scene.frame_current == shot_strip_1.frame_final_start


def test_bidirectional_outside_shot_range_to_surrounding_shots(basic_synced_setup):
    edit_scene, shot_strip_1 = basic_synced_setup
    edit_scene.frame_set(shot_strip_1.frame_final_start)
    # Create another Shot right after Shot 1
    shot_strip_2 = create_shot_scene(edit_scene, 1, shot_strip_1.frame_final_end)

    # From frame start, go outside scene's range within Shot 1 by one frame
    shot_strip_1.scene.frame_set(shot_strip_1.scene.frame_end + 1)
    # This should not update current scene, as we did not pass trough end frame
    assert bpy.context.window.scene == shot_strip_1.scene
    # Now, go to the end of Shot 1 first
    shot_strip_1.scene.frame_set(shot_strip_1.scene.frame_end)
    # Go outside scene's range within Shot 1 by one frame
    shot_strip_1.scene.frame_set(shot_strip_1.scene.frame_end + 1)
    # Master time should have been update and Shot 2 should now be the active Shot
    assert edit_scene.frame_current == shot_strip_2.frame_final_start
    assert bpy.context.window.scene == shot_strip_2.scene

    # Go back one frame before Shot 2 frame start
    shot_strip_2.scene.frame_set(shot_strip_2.scene.frame_start - 1)
    # Master time should have been updated and Shot 1 should not be active again
    assert edit_scene.frame_current == shot_strip_1.frame_final_end - 1
    assert bpy.context.window.scene == shot_strip_1.scene


def test_bidirectional_off(basic_synced_setup):
    edit_scene, shot_strip_1 = basic_synced_setup
    sync_settings = get_sync_settings()
    sync_settings.bidirectional = False

    edit_scene.frame_set(shot_strip_1.frame_final_start)
    shot_strip_1.scene.frame_set(shot_strip_1.scene.frame_current + 10)
    assert edit_scene.frame_current == shot_strip_1.frame_final_start


def test_camera_strip(basic_synced_setup):
    edit_scene, shot_strip_1 = basic_synced_setup
    shot_scene = shot_strip_1.scene

    # Create 2 cameras in the shot scene
    cam1_data = bpy.data.cameras.new(name="Cam1")
    cam1 = bpy.data.objects.new(name="Cam1", object_data=cam1_data)
    cam2_data = bpy.data.cameras.new(name="Cam2")
    cam2 = bpy.data.objects.new(name="Cam2", object_data=cam2_data)
    shot_scene.collection.objects.link(cam1)
    shot_scene.collection.objects.link(cam2)

    # Create a new strip poiting to the same scene
    shot_strip_2 = edit_scene.sequence_editor.sequences.new_scene(
        name=f"{shot_scene.name}_2",
        scene=shot_scene,
        channel=1,
        frame_start=shot_strip_1.frame_final_end,
    )

    # Define different cameras for each strip
    shot_strip_1.scene_camera = cam1
    shot_strip_2.scene_camera = cam2

    # Go to 1st strip: the scene should be using cam1 as active camera
    edit_scene.frame_set(shot_strip_1.frame_final_start)
    assert shot_scene.camera == shot_strip_1.scene_camera == cam1
    # Go to 2n strip: the scene should be using cam1 as active camera
    edit_scene.frame_set(shot_strip_2.frame_final_start)
    assert shot_scene.camera == shot_strip_2.scene_camera == cam2


def test_skip_muted_strips(complex_synced_setup):
    edit_scene, shots = complex_synced_setup

    # Test Strip 4 is active
    edit_scene.frame_set(1)
    assert bpy.context.window.scene == shots[3].scene

    # Mute Channel 4 and check if Strip 3 is active
    edit_scene.sequence_editor.channels[4].mute = True
    edit_scene.frame_set(2)
    assert bpy.context.window.scene == shots[2].scene

    #  Mute Strip 3 and check if Strip 2 is active
    shots[2].mute = True
    edit_scene.frame_set(3)
    assert bpy.context.window.scene == shots[1].scene


def test_active_follows_playhead(basic_synced_setup):
    edit_scene, shot_strip_1 = basic_synced_setup

    edit_scene.sequence_editor.active_strip = shot_strip_1

    sync_settings = get_sync_settings()
    sync_settings.active_follows_playhead = True

    shot_strip_2 = create_shot_scene(edit_scene, 1, shot_strip_1.frame_final_end + 1)

    edit_scene.frame_set(shot_strip_2.frame_final_start)
    assert edit_scene.sequence_editor.active_strip == shot_strip_2
