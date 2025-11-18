#!/usr/bin/env python3
"""
Base Mesh Generator for The Penitent Mechanism - V4.0
Imports high-quality human base mesh and adapts it for the avatar

ARCHITECTURE:
- Imports pre-modeled human base mesh (human_base_mesh.blend)
- Applies scale and pose adjustments for kneeling statue aesthetic
- Saves as reusable base for kitbashing mechanical parts

This uses a proper anatomical mesh with professional topology
instead of generating from primitives or skin modifier.
"""

import bpy
import bmesh
import math
import os
from mathutils import Vector

# Input: Human base mesh from root repo (stored in Git LFS)
INPUT_PATH = os.path.abspath("human_base_mesh.blend")
OUTPUT_PATH = "Avatar/BaseMeshes/PenitentMechanism_Base.blend"

def clear_scene():
    """Remove all default objects"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    # Clear orphan data
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)

    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)

    for block in bpy.data.armatures:
        if block.users == 0:
            bpy.data.armatures.remove(block)

def import_human_base():
    """Import the human base mesh from the source file"""
    print(f"Importing human base mesh from: {INPUT_PATH}")

    if not os.path.exists(INPUT_PATH):
        raise FileNotFoundError(f"Human base mesh not found: {INPUT_PATH}")

    # Check file size to ensure it's not just an LFS pointer
    file_size = os.path.getsize(INPUT_PATH)
    if file_size < 1000:  # LFS pointers are tiny
        raise RuntimeError(
            f"File appears to be a Git LFS pointer ({file_size} bytes). "
            "Run 'git lfs pull' to download the actual file."
        )

    # Import all objects from the blend file
    with bpy.data.libraries.load(INPUT_PATH, link=False) as (data_from, data_to):
        data_to.objects = data_from.objects
        data_to.armatures = data_from.armatures

    # Link imported objects to scene
    imported_meshes = []
    imported_armatures = []

    for obj in data_to.objects:
        if obj is not None:
            bpy.context.collection.objects.link(obj)
            if obj.type == 'MESH':
                imported_meshes.append(obj)
                print(f"  ✓ Imported mesh: {obj.name} ({len(obj.data.vertices)} verts)")
            elif obj.type == 'ARMATURE':
                imported_armatures.append(obj)
                print(f"  ✓ Imported armature: {obj.name}")

    if not imported_meshes:
        raise RuntimeError("No mesh objects found in human_base_mesh.blend")

    # Find the main body mesh (largest vertex count)
    main_mesh = max(imported_meshes, key=lambda o: len(o.data.vertices))
    print(f"\n  Main body mesh: {main_mesh.name}")

    return main_mesh, imported_meshes, imported_armatures

def prepare_base_mesh(main_mesh, all_meshes, armatures):
    """
    Prepare the imported mesh for use as avatar base.
    - Scale to appropriate size
    - Center and position
    - Clean up
    """
    print("\nPreparing base mesh...")

    # Select all imported objects
    bpy.ops.object.select_all(action='DESELECT')
    for obj in all_meshes:
        obj.select_set(True)
    for arm in armatures:
        arm.select_set(True)

    bpy.context.view_layer.objects.active = main_mesh

    # Reset transforms first
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Get current bounds
    min_z = min(v.co.z for v in main_mesh.data.vertices)
    max_z = max(v.co.z for v in main_mesh.data.vertices)
    current_height = max_z - min_z

    # Target height for kneeling pose (approximately 1.0-1.2m for kneeling figure)
    # The full standing height would be ~1.8m
    target_height = 1.2

    if current_height > 0:
        scale_factor = target_height / current_height
        print(f"  Scaling from {current_height:.2f}m to {target_height:.2f}m (factor: {scale_factor:.3f})")

        # Apply uniform scale
        for obj in all_meshes + armatures:
            obj.scale = (scale_factor, scale_factor, scale_factor)

        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Recalculate bounds after scaling
    min_z = min(v.co.z for v in main_mesh.data.vertices)

    # Move so feet are at ground level (z=0)
    z_offset = -min_z
    for obj in all_meshes + armatures:
        obj.location.z += z_offset

    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Center on X and Y
    bounds_min = Vector((float('inf'), float('inf'), float('inf')))
    bounds_max = Vector((float('-inf'), float('-inf'), float('-inf')))

    for v in main_mesh.data.vertices:
        for i in range(3):
            bounds_min[i] = min(bounds_min[i], v.co[i])
            bounds_max[i] = max(bounds_max[i], v.co[i])

    center_x = (bounds_min.x + bounds_max.x) / 2
    center_y = (bounds_min.y + bounds_max.y) / 2

    for obj in all_meshes + armatures:
        obj.location.x -= center_x
        obj.location.y -= center_y

    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    print(f"  ✓ Mesh positioned at origin, grounded at z=0")

    return main_mesh

def finalize_base_mesh(main_mesh, all_meshes):
    """
    Final cleanup and preparation for export.
    """
    print("\nFinalizing base mesh...")

    # Rename main mesh
    main_mesh.name = "PenitentMechanism_Base"
    if main_mesh.data:
        main_mesh.data.name = "PenitentMechanism_Base"

    # Clean up geometry
    bpy.context.view_layer.objects.active = main_mesh
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=0.0001)
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Smooth shading
    bpy.ops.object.shade_smooth()
    main_mesh.data.use_auto_smooth = True
    main_mesh.data.auto_smooth_angle = math.radians(30)

    # Remove any other mesh objects (keep only main body)
    for obj in all_meshes:
        if obj != main_mesh:
            bpy.data.objects.remove(obj, do_unlink=True)

    print(f"  ✓ Finalized: {main_mesh.name}")

    return main_mesh

def main():
    """Import and prepare human base mesh for avatar generation"""
    print("=" * 70)
    print("BASE MESH GENERATOR V4.0 - The Penitent Mechanism")
    print("Importing pre-modeled human base mesh")
    print("=" * 70)

    print("\n[1/4] Clearing scene...")
    clear_scene()

    print("\n[2/4] Importing human base mesh...")
    main_mesh, all_meshes, armatures = import_human_base()

    print("\n[3/4] Preparing base mesh...")
    main_mesh = prepare_base_mesh(main_mesh, all_meshes, armatures)

    print("\n[4/4] Finalizing...")
    basemesh = finalize_base_mesh(main_mesh, all_meshes)

    # Final statistics
    print(f"\n{'='*70}")
    print("BASE MESH READY")
    print('='*70)
    print(f"  Name: {basemesh.name}")
    print(f"  Vertices: {len(basemesh.data.vertices)}")
    print(f"  Faces: {len(basemesh.data.polygons)}")
    print(f"  Triangles: {sum(len(p.vertices) - 2 for p in basemesh.data.polygons)}")

    # Calculate bounds
    min_z = min(v.co.z for v in basemesh.data.vertices)
    max_z = max(v.co.z for v in basemesh.data.vertices)
    print(f"  Height: {max_z - min_z:.2f}m")

    print(f"\nSaving to: {OUTPUT_PATH}")
    bpy.ops.wm.save_as_mainfile(filepath=OUTPUT_PATH)
    print("✓ Base mesh saved!")

    print("\n" + "=" * 70)
    print("✓ BASE MESH IMPORT COMPLETE!")
    print("High-quality anatomical mesh ready for kitbashing.")
    print("=" * 70)

if __name__ == "__main__":
    main()
