# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2023, The SPA Studios. All rights reserved.

import pytest

import bpy

from spa_sequencer.shot.core import (
    adjust_shot_duration,
    delete_scene,
    duplicate_scene,
    DuplicationManifest,
    rename_scene,
    slip_shot_content,
)


from utils import create_shot_scene


def test_scene_duplication_same_name():
    ref_scene = bpy.context.scene
    with pytest.raises(ValueError):
        duplicate_scene(bpy.context, ref_scene, ref_scene.name)


def test_scene_duplication():
    ref_scene = bpy.context.scene
    # Create a new scene named "SceneCopy"
    new_scene = duplicate_scene(bpy.context, ref_scene, "SceneCopy")

    # Check collection duplication
    assert len(new_scene.collection.children) == len(ref_scene.collection.children)
    # Check object duplication
    assert len(new_scene.objects) == len(ref_scene.objects)
    # Check data duplication
    assert ref_scene.objects[0].data != new_scene.objects[0].data

    # Add an object to "SceneCopy"'s root collection
    obj_name = "Empty_{}"
    new_obj = bpy.data.objects.new(
        name=obj_name.format(new_scene.name), object_data=None
    )
    new_scene.collection.objects.link(new_obj)
    # Create another scene from "SceneCopy"
    new_scene2 = duplicate_scene(bpy.context, new_scene, "SceneCopy2")
    # Check that this last scene has been created from "SceneCopy"
    assert len(new_scene2.objects) == len(new_scene.objects) != len(ref_scene.objects)
    # Check datablack auto-renaming
    assert obj_name.format(new_scene2.name) in new_scene2.objects


def test_scene_duplication_animation_data():
    ref_scene = bpy.context.scene

    # Keyframe active object
    ref_obj = ref_scene.view_layers[0].objects.active
    ref_obj.keyframe_insert(data_path="location", frame=1)

    # Duplicate the scene
    new_scene = duplicate_scene(bpy.context, ref_scene, "SceneCopy")

    # Ensure new scene's active object has animation data
    new_obj = new_scene.view_layers[0].objects.active
    assert new_obj.animation_data and new_obj.animation_data.action

    ref_action = ref_obj.animation_data.action
    new_action = new_obj.animation_data.action
    # Check action duplication
    assert ref_action != new_action
    # Check that fcurves are preserved
    assert len(ref_action.fcurves) == len(new_action.fcurves)


def test_scene_duplication_hierarchy():
    ref_scene = bpy.context.scene

    # Create a few objects and link them to the active scene collection
    obj1 = bpy.data.objects.new(name="Obj1", object_data=None)
    obj2 = bpy.data.objects.new(name="Obj2", object_data=None)
    obj3 = bpy.data.objects.new(name="Obj3", object_data=None)

    ref_scene.collection.objects.link(obj1)
    ref_scene.collection.objects.link(obj2)
    ref_scene.collection.objects.link(obj3)

    # Parent source objects
    obj3.parent = obj2
    obj2.parent = obj1

    # Duplicate the active scene
    manifest = DuplicationManifest()
    duplicate_scene(bpy.context, ref_scene, "SceneCopy", manifest)

    # Ensure parenting hierarchy is preserved
    assert manifest[obj2].parent == manifest[obj1]
    assert manifest[obj3].parent == manifest[obj2]


def test_scene_duplication_modifier_remapping():
    ref_scene = bpy.context.scene

    # Create a modifier with a reference to an object in the scene
    obj = bpy.context.active_object
    mod = obj.modifiers.new(name="Cast", type="CAST")
    mod.object = bpy.context.scene.camera

    # Duplicate the scene
    manifest = DuplicationManifest()
    duplicate_scene(bpy.context, ref_scene, "SceneCopy", manifest)

    # Ensure modifier's object reference has been remapped
    assert manifest[obj].modifiers[0].object == manifest[mod.object]


def test_scene_duplication_constraint_remapping():
    ref_scene = bpy.context.scene

    # Create a constraint with a reference to an object in the scene
    obj = bpy.context.active_object
    constraint = obj.constraints.new(type="TRACK_TO")
    constraint.target = bpy.context.scene.camera

    # Duplicate the scene
    manifest = DuplicationManifest()
    duplicate_scene(bpy.context, ref_scene, "SceneCopy", manifest)

    # Ensure constraint's target has been remapped
    assert manifest[obj].constraints[0].target == manifest[constraint.target]


def test_scene_duplication_driver_remapping():
    ref_scene = bpy.context.scene

    obj = bpy.context.active_object
    # Create a driver with targets referencing object and data
    fcurve = obj.driver_add("location", 0)
    driver = fcurve.driver
    varA = driver.variables.new()
    varA.targets[0].id_type = "OBJECT"
    varA.targets[0].id = bpy.context.scene.camera
    varB = driver.variables.new()
    varB.targets[0].id_type = "CAMERA"
    varB.targets[0].id = bpy.context.scene.camera.data

    # Duplicate the scene
    manifest = DuplicationManifest()
    duplicate_scene(bpy.context, ref_scene, "SceneCopy", manifest)

    # Ensure duplicated driver's targets references have been remapped
    new_driver = manifest[obj].animation_data.drivers[0].driver
    assert new_driver.variables[0].targets[0].id == manifest[varA.targets[0].id]
    assert new_driver.variables[1].targets[0].id == manifest[varB.targets[0].id]


def test_scene_duplication_gp_modifier_and_effect_remapping():
    ref_scene = bpy.context.scene

    # Create a GP object with modifier and FX referencing an object in the scene
    bpy.ops.object.add(type="GPENCIL")
    obj = bpy.context.active_object
    mod = obj.grease_pencil_modifiers.new(name="Mirror", type="GP_MIRROR")
    mod.object = bpy.context.scene.camera
    fx = obj.shader_effects.new(name="Shadow", type="FX_SHADOW")
    fx.object = bpy.context.scene.camera

    # Duplicate the scene
    manifest = DuplicationManifest()
    duplicate_scene(bpy.context, ref_scene, "SceneCopy", manifest)

    # Ensure GP modifier and effect's object references have been remapped
    assert manifest[obj].grease_pencil_modifiers[0].object == manifest[mod.object]
    assert manifest[obj].shader_effects[0].object == manifest[fx.object]


def test_scene_rename_empty_object():
    scene = bpy.context.scene
    # Create an object without data and add scene name to its name
    bpy.ops.object.add(type="EMPTY")
    bpy.context.active_object.name += f".{scene.name}"

    # Rename the scene
    new_scene_name = "SceneRenamed"
    rename_scene(scene, new_scene_name)

    # Ensure the active object was properly renamed
    assert bpy.context.active_object.name.endswith(new_scene_name)


def test_scene_rename_datablocks():
    scene = bpy.context.scene
    new_name = "Shot"

    # Append the scene's name to all datablocks in active collection
    suffix = f"{scene.name}"
    col = bpy.context.collection

    col.name += suffix

    for obj in col.objects:
        # Create an animation to trigger the creation of an action
        obj.keyframe_insert(data_path="location", frame=1)
        obj.name += suffix
        obj.data.name += suffix
        obj.animation_data.action.name += suffix

    # Rename the scene
    rename_scene(scene, new_name)

    # Ensure all datablocks have been properly renamed
    assert scene.name == new_name
    assert col.name.endswith(new_name)
    for obj in col.objects:
        for datablock in (obj, obj.data, obj.animation_data.action):
            assert datablock.name.endswith(new_name)


def test_scene_rename_invalid_name():
    ref_scene_name = bpy.context.scene.name

    bpy.ops.scene.new(type="EMPTY")

    # Ensure using an already existing scene name fails
    with pytest.raises(ValueError):
        rename_scene(bpy.context.scene, ref_scene_name)


def test_scene_delete_scene_duplicate():
    # Duplicate the default scene
    manifest = DuplicationManifest()
    sceneA = duplicate_scene(bpy.context, bpy.context.scene, "SceneA", manifest)

    # Delete this new scene
    del_count = delete_scene(sceneA, True)

    # Ensure by count that all created datablocks were deleted
    assert del_count == len(manifest)
    # Iterate over manifest and ensure that all datablocks were deleted.
    # Accessing them must throw a ReferenceError.
    for datablock in manifest.values():
        with pytest.raises(ReferenceError):
            getattr(datablock, "bl_rna")


def test_scene_delete_scene_duplicate_with_shared_collection():
    # Duplicate default scene
    manifest = DuplicationManifest()
    sceneA = duplicate_scene(bpy.context, bpy.context.scene, "SceneA", manifest)
    # Link a collection from the default scene into the new scene
    shared_col = bpy.context.scene.collection.children[0]
    sceneA.collection.children.link(shared_col)

    # Delete the scene
    del_count = delete_scene(sceneA, True)

    # Ensure that only datablocks from the duplication process were deleted
    assert del_count == len(manifest)
    for datablock in manifest.values():
        with pytest.raises(ReferenceError):
            getattr(datablock, "bl_rna")

    # The shared collection should still be valid
    assert shared_col.bl_rna


def test_shot_duration_adjust_positive_offset():
    # Create a shot
    sh1 = create_shot_scene(bpy.context.scene, 1, 1)
    sh1_original_duration = sh1.frame_final_duration

    # Adjust duration: use a positive offset
    offset = 10
    adjust_shot_duration(sh1, offset)

    # Strip's final duration and internal scene range should have been impacted
    assert sh1.frame_final_duration == sh1_original_duration + offset
    assert sh1.scene.frame_end == sh1.scene.frame_start + sh1.frame_final_duration - 1


def test_shot_duration_adjust_negative_offset():
    # Create a shot
    sh1 = create_shot_scene(bpy.context.scene, 1, 1)
    original_frame_end = sh1.scene.frame_end

    # Adjust duration: use a negative offset
    sh1_new_duration = 10
    offset = sh1_new_duration - sh1.frame_final_duration
    adjust_shot_duration(sh1, offset)

    # Strip's final duration should have been impacted
    assert sh1.frame_final_duration == sh1_new_duration
    # Internal scene range should have been preserved (shorter duration)
    assert sh1.scene.frame_end == original_frame_end


def test_shot_duration_adjust_negative_offset_clamp():
    # Create a shot
    sh1 = create_shot_scene(bpy.context.scene, 1, 1)
    original_frame_end = sh1.scene.frame_end

    # Adjust duration: use a negative offset leading to a null duration
    sh1_new_duration = 0
    offset = sh1_new_duration - sh1.frame_final_duration
    adjust_shot_duration(sh1, offset)

    # Duration should have been clamped to 1
    assert sh1.frame_final_duration == 1
    # Internal scene range should have been preserved (shorter duration)
    assert sh1.scene.frame_end == original_frame_end


def test_shot_duration_adjust_from_start_negative_offset():
    # Create a shot
    sh1 = create_shot_scene(bpy.context.scene, 1, 1)

    duration = sh1.frame_final_duration
    # Adjust duration from frame start
    offset = -10
    adjust_shot_duration(sh1, offset, from_frame_start=True)

    # Strip start frame should not have changed
    assert sh1.frame_final_start == 1
    # Strip content should have been offset
    assert sh1.frame_offset_start == -offset
    assert sh1.frame_final_duration == duration + offset


def test_shot_duration_adjust_from_start_negative_offset_clamp():
    # Create a shot
    sh1 = create_shot_scene(bpy.context.scene, 1, 1)

    duration = sh1.frame_final_duration
    # Adjust duration from frame start with an offset going above frame end
    offset = -duration * 2
    adjust_shot_duration(sh1, offset, from_frame_start=True)

    # Strip start frame should not have changed
    assert sh1.frame_final_start == 1
    # Strip content offset should have been clamped to have a minimum duration of 1
    assert sh1.frame_offset_start == duration - 1
    assert sh1.frame_final_duration == 1


def test_shot_duration_adjust_from_start_positive_offset_clamp():
    # Create a shot
    sh1 = create_shot_scene(bpy.context.scene, 1, 1)

    duration = sh1.frame_final_duration
    # Adjust duration from frame start with a positive offset going above strip's
    # scene frame start.
    offset = 1
    adjust_shot_duration(sh1, offset, from_frame_start=True)

    # Strip start frame should not have changed
    assert sh1.frame_final_start == 1
    # Offset should have been clamped to stay in scene's range
    assert sh1.frame_offset_start == 0
    # Duration should not have changed
    assert sh1.frame_final_duration == duration


def test_shot_duration_adjust_with_multiple_shots():
    # Create a sequence with 3 shots following each others
    sh1 = create_shot_scene(bpy.context.scene, 1, bpy.context.scene.frame_start)
    sh2 = create_shot_scene(bpy.context.scene, 1, sh1.frame_final_end)
    sh3 = create_shot_scene(bpy.context.scene, 1, sh2.frame_final_end)

    # Retime the shot in between
    sh2_original_frame_end = sh2.frame_final_end
    offset = 10
    adjust_shot_duration(sh2, offset)

    # 1st shot should not have been impacted
    assert sh1.frame_final_start == bpy.context.scene.frame_start
    # 2nd shot's duration should have changed
    assert sh2.frame_final_end == sh2_original_frame_end + offset
    # 3rd shot should have been shifted
    assert sh3.frame_final_start == sh2.frame_final_end


def test_shot_slip_content_positive_offset():
    # Test strip
    sh1 = create_shot_scene(bpy.context.scene, 1, bpy.context.scene.frame_start)
    # Witness strip
    sh2 = create_shot_scene(bpy.context.scene, 2, bpy.context.scene.frame_start)

    offset = 10
    slip_shot_content(sh2, offset)

    # Ensure strip frame_start members were propertly updated
    assert sh2.frame_offset_start == sh1.frame_offset_start + offset
    assert sh2.frame_start == sh1.frame_start - offset
    assert sh2.frame_final_start == sh1.frame_final_start


def test_shot_slip_content_negative_offset():
    # Test strip
    sh1 = create_shot_scene(bpy.context.scene, 1, bpy.context.scene.frame_start)
    # Witness strip
    sh2 = create_shot_scene(bpy.context.scene, 2, bpy.context.scene.frame_start)

    offset = -10

    # Strip's internal range start at internal frame start.
    # With clamp_start enabled, this sould not change anything.
    slip_shot_content(sh2, offset, clamp_start=True)
    assert sh2.frame_offset_start == sh1.frame_offset_start
    assert sh2.frame_start == sh1.frame_start
    assert sh2.frame_final_start == sh1.frame_final_start

    # Without clamp, offset should have been applied
    slip_shot_content(sh2, offset, clamp_start=False)
    assert sh2.frame_offset_start == sh1.frame_offset_start + offset
    assert sh2.frame_start == sh1.frame_start - offset
    assert sh2.frame_final_start == sh1.frame_final_start
