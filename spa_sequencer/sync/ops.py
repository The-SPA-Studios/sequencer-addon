# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2023, The SPA Studios. All rights reserved.

import bpy

from spa_sequencer.sync.core import get_sync_settings, sync_system_update

from spa_sequencer.utils import register_classes, unregister_classes


class WM_OT_timeline_sync_toggle(bpy.types.Operator):
    bl_idname = "wm.timeline_sync_toggle"
    bl_label = "Toggle Timeline Synchronization"
    bl_description = "Toggle Timeline Synchronization System"
    bl_options = set()

    def execute(self, context: bpy.types.Context):
        sync_settings = get_sync_settings()
        sync_settings.enabled = not sync_settings.enabled

        # NOTE: The following code block will only be executed
        #       if we are running a SPA version of Blender
        #       (https://github.com/The-SPA-Studios/blender)
        #       that allows for scene overrides on a space.
        if hasattr(context.space_data, "scene_override"):
            # Setup with active space's data if applicable
            if (
                sync_settings.enabled
                and isinstance(context.space_data, bpy.types.SpaceSequenceEditor)
                and context.space_data.scene_override
            ):
                # Use overriden scene defined in the SpaceSequence editor as master scene
                sync_settings.master_scene = context.space_data.scene_override

        # Trigger sync system update
        sync_system_update(context)

        return {"FINISHED"}


class WM_OT_timeline_sync_play_master(bpy.types.Operator):
    bl_idname = "wm.timeline_sync_play_master"
    bl_label = "Play Master Scene"
    bl_description = "Toggle playback of master scene"
    bl_options = set()

    bl_keymaps = [
        {
            "space_type": "EMPTY",
            "category_name": "Frames",
            "key": "SPACE",
            "shift": True,
        }
    ]

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return get_sync_settings().master_scene is not None

    def execute(self, context: bpy.types.Context):
        # TODO Improve this by using a pointer to find the main window instead
        master_scene = get_sync_settings().master_scene
        for window in context.window_manager.windows:
            if window.scene == master_scene:
                master_window = window
        # Trigger playback on master scene using context override.
        with context.temp_override(
            window=master_window,
            scene=get_sync_settings().master_scene,
        ):
            bpy.ops.screen.animation_play(sync=True)
        return {"FINISHED"}


classes = (
    WM_OT_timeline_sync_toggle,
    WM_OT_timeline_sync_play_master,
)


def register():
    register_classes(classes)


def unregister():
    unregister_classes(classes)
