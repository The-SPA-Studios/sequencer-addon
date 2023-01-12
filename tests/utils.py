# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2023, The SPA Studios. All rights reserved.

import bpy


def create_shot_scene(
    edit_scene: bpy.types.Scene, channel: int, frame_start: int
) -> bpy.types.SceneSequence:
    """
    Create a new empty scene and adds it as a strip in `edit_scene`'s sequence editor.

    :param edit_scene: The edit scene
    :param channel: Shot strip's channel
    :param frame_start: Shot strip's frame start
    :return: The created shot strip
    """
    # Create a new scene
    shot_scene = bpy.data.scenes.new(name="SHOT")
    # Add a scene strip in the edit scene's sequence editor
    shot_strip = edit_scene.sequence_editor.sequences.new_scene(
        name=shot_scene.name,
        scene=shot_scene,
        channel=channel,
        frame_start=frame_start,
    )
    return shot_strip
