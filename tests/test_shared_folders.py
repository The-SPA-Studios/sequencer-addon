# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2023, The SPA Studios. All rights reserved.

import pytest

import bpy

from spa_sequencer.shared_folders import core


def test_shared_folders_root():
    # Initially, the root collection does not exist
    assert core.get_shared_folders_root_collection() is None
    # Create it and ensure it's valid
    root_collection = core.get_or_create_shared_folders_root_collection()
    assert core.get_shared_folders_root_collection() == root_collection


def test_make_shared_folder_from_collection():
    # Turn a collection in the default scene into a share collection
    col = bpy.context.scene.collection.children[0]
    core.make_shared_folder_from_collection(col)
    # Ensure it is considered as such
    assert core.is_shared_folder(col)


def test_make_shared_folder_from_scene_collection():
    # Ensure a scene's master collection cannot be used as a shared folder
    with pytest.raises(ValueError):
        core.make_shared_folder_from_collection(bpy.context.scene.collection)


def test_create_new_shared_folder():
    # Create a new shared folder from a name
    folder_name = "SharedFolder"
    collection = core.create_shared_folder(folder_name)
    # Ensure it has been properly registered as a shared collection
    assert core.is_shared_folder(collection)
    assert core.get_shared_folder_by_name(folder_name) == collection


def test_get_invalid_shared_folder():
    # The root collection for shared folder does not exist, this raises RuntimeError
    with pytest.raises(RuntimeError):
        core.get_shared_folder_by_name("FakeFolder")

    # Create the root collection
    core.get_or_create_shared_folders_root_collection()

    # The shared folder does not exist, this raises ValueError
    with pytest.raises(ValueError):
        core.get_shared_folder_by_name("FakeFolder")


def test_link_in_scene():
    # Create a shared folder from existing collection
    col = bpy.context.scene.collection.children[0]
    core.make_shared_folder_from_collection(col)
    # Link it to the current scene
    core.link_shared_folder(col, [bpy.context.scene])
    # Ensure the collection is linked in the scene's collection
    assert col in bpy.context.scene.collection.children.values()


def test_create_and_link_in_scene():
    # Create a shared folder and link it in current scene
    col, _ = core.create_and_link_shared_folder("SharedFolder", [bpy.context.scene])

    # Ensure collection is a shared folder and that it is linked in the scene
    assert core.is_shared_folder(col)
    assert col in bpy.context.scene.collection.children.values()


def test_create_link_unlink_in_multiple_scenes():
    # Create several scenes
    scenes = [bpy.data.scenes.new(name=f"Scene{i}") for i in range(3)]

    # Create a shared folder and link it in those scenes
    col, _ = core.create_and_link_shared_folder("SharedFolder", scenes)
    assert core.is_shared_folder(col)

    # Ensure the collection is in each scene's collection
    for scene in scenes:
        assert col in scene.collection.children.values()

    # This should not raise (but does not do anything)
    core.link_shared_folder(col, scenes)

    # Unlink shared folders
    core.unlink_shared_folder(col, scenes)

    for scene in scenes:
        assert col not in scene.collection.children.values()

    # The only user left should be the shared folder root collection
    assert col.users == 1


def test_delete_shared_folder():
    folder_name = "SharedFolder"
    collection = core.create_shared_folder(folder_name)
    core.delete_shared_folder(collection)

    with pytest.raises(ReferenceError):
        getattr(collection, "name")

    with pytest.raises(ValueError):
        core.get_shared_folder_by_name(folder_name)
