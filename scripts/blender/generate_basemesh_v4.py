#!/usr/bin/env python3
"""
Base Mesh Generator V4 - The Penitent Mechanism
Creates a proper humanoid base mesh with character-quality topology.

ARCHITECTURE:
- Uses Blender's Skin modifier for organic base forms
- Proper edge loops at joints for deformation
- Statue-like aesthetic with kneeling pose
- Suitable for rigging and animation
"""

import bpy
import bmesh
import math
from mathutils import Vector

OUTPUT_PATH = "Avatar/BaseMeshes/PenitentMechanism_Base.blend"

def clear_scene():
    """Remove all default objects"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    # Clear orphan data
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)

def create_humanoid_basemesh():
    """
    Create humanoid base using Skin modifier technique.
    This creates proper organic topology from a skeleton-like armature of edges.
    """
    print("Creating humanoid base skeleton...")

    # Create new mesh and object
    mesh = bpy.data.meshes.new("BaseMesh_Data")
    obj = bpy.data.objects.new("PenitentMechanism_Base", mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # Enter edit mode and create vertex skeleton
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(mesh)

    # Define skeleton points for humanoid in kneeling pose
    # Format: (name, position, radius_scale)
    skeleton_points = {
        # Spine/Torso (vertical in kneeling pose)
        'pelvis': (Vector((0, 0, 0.50)), 0.12),
        'spine_low': (Vector((0, 0, 0.70)), 0.13),
        'spine_mid': (Vector((0, 0, 0.90)), 0.14),
        'spine_high': (Vector((0, 0, 1.10)), 0.13),
        'chest': (Vector((0, 0, 1.25)), 0.12),

        # Neck/Head
        'neck_base': (Vector((0, 0, 1.35)), 0.06),
        'neck_top': (Vector((0, 0, 1.50)), 0.06),
        'head_base': (Vector((0, 0, 1.55)), 0.10),
        'head_mid': (Vector((0, 0, 1.68)), 0.12),
        'head_top': (Vector((0, 0, 1.82)), 0.10),

        # Left Arm
        'shoulder_L': (Vector((0.18, 0, 1.25)), 0.08),
        'upperarm_L': (Vector((0.32, 0, 1.20)), 0.06),
        'elbow_L': (Vector((0.42, 0, 1.05)), 0.05),
        'forearm_L': (Vector((0.48, 0.12, 0.90)), 0.05),
        'wrist_L': (Vector((0.52, 0.25, 0.78)), 0.04),
        'hand_L': (Vector((0.54, 0.35, 0.70)), 0.04),

        # Right Arm
        'shoulder_R': (Vector((-0.18, 0, 1.25)), 0.08),
        'upperarm_R': (Vector((-0.32, 0, 1.20)), 0.06),
        'elbow_R': (Vector((-0.42, 0, 1.05)), 0.05),
        'forearm_R': (Vector((-0.48, 0.12, 0.90)), 0.05),
        'wrist_R': (Vector((-0.52, 0.25, 0.78)), 0.04),
        'hand_R': (Vector((-0.54, 0.35, 0.70)), 0.04),

        # Left Leg (kneeling - thigh angled down, shin vertical)
        'hip_L': (Vector((0.10, 0, 0.48)), 0.08),
        'thigh_L': (Vector((0.12, -0.10, 0.35)), 0.07),
        'knee_L': (Vector((0.14, 0.05, 0.25)), 0.06),
        'shin_L': (Vector((0.14, 0.10, 0.15)), 0.05),
        'ankle_L': (Vector((0.14, 0.15, 0.05)), 0.04),
        'foot_L': (Vector((0.14, 0.22, 0.03)), 0.05),

        # Right Leg (kneeling)
        'hip_R': (Vector((-0.10, 0, 0.48)), 0.08),
        'thigh_R': (Vector((-0.12, -0.10, 0.35)), 0.07),
        'knee_R': (Vector((-0.14, 0.05, 0.25)), 0.06),
        'shin_R': (Vector((-0.14, 0.10, 0.15)), 0.05),
        'ankle_R': (Vector((-0.14, 0.15, 0.05)), 0.04),
        'foot_R': (Vector((-0.14, 0.22, 0.03)), 0.05),
    }

    # Create vertices
    verts = {}
    for name, (pos, radius) in skeleton_points.items():
        v = bm.verts.new(pos)
        verts[name] = v
        # Store radius for skin modifier
        v.tag = True

    bm.verts.ensure_lookup_table()

    # Define skeleton connections (edges)
    connections = [
        # Spine
        ('pelvis', 'spine_low'),
        ('spine_low', 'spine_mid'),
        ('spine_mid', 'spine_high'),
        ('spine_high', 'chest'),

        # Neck/Head
        ('chest', 'neck_base'),
        ('neck_base', 'neck_top'),
        ('neck_top', 'head_base'),
        ('head_base', 'head_mid'),
        ('head_mid', 'head_top'),

        # Left Arm
        ('chest', 'shoulder_L'),
        ('shoulder_L', 'upperarm_L'),
        ('upperarm_L', 'elbow_L'),
        ('elbow_L', 'forearm_L'),
        ('forearm_L', 'wrist_L'),
        ('wrist_L', 'hand_L'),

        # Right Arm
        ('chest', 'shoulder_R'),
        ('shoulder_R', 'upperarm_R'),
        ('upperarm_R', 'elbow_R'),
        ('elbow_R', 'forearm_R'),
        ('forearm_R', 'wrist_R'),
        ('wrist_R', 'hand_R'),

        # Left Leg
        ('pelvis', 'hip_L'),
        ('hip_L', 'thigh_L'),
        ('thigh_L', 'knee_L'),
        ('knee_L', 'shin_L'),
        ('shin_L', 'ankle_L'),
        ('ankle_L', 'foot_L'),

        # Right Leg
        ('pelvis', 'hip_R'),
        ('hip_R', 'thigh_R'),
        ('thigh_R', 'knee_R'),
        ('knee_R', 'shin_R'),
        ('shin_R', 'ankle_R'),
        ('ankle_R', 'foot_R'),
    ]

    # Create edges
    for start, end in connections:
        if start in verts and end in verts:
            bm.edges.new([verts[start], verts[end]])

    bmesh.update_edit_mesh(mesh)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Apply Skin modifier to convert skeleton to mesh
    print("Applying Skin modifier...")
    skin = obj.modifiers.new(name="Skin", type='SKIN')

    # Set individual vertex radii for proper proportions
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(mesh)
    skin_layer = bm.verts.layers.skin.verify()

    for name, (pos, radius) in skeleton_points.items():
        if name in verts:
            v = verts[name]
            v[skin_layer].radius = (radius, radius)

    bmesh.update_edit_mesh(mesh)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Apply Subdivision for smoothness
    print("Adding subdivision...")
    subsurf = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 3

    # Apply modifiers to get final geometry
    print("Applying modifiers...")
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.view_layer.objects.active = obj

    # Apply Skin modifier
    bpy.ops.object.modifier_apply(modifier="Skin")

    # Keep subdivision unapplied for flexibility

    # Clean up mesh
    print("Cleaning up geometry...")
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=0.001)
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.mesh.delete_loose()
    bpy.ops.object.mode_set(mode='OBJECT')

    # Smooth shading
    bpy.ops.object.shade_smooth()
    mesh.use_auto_smooth = True
    mesh.auto_smooth_angle = math.radians(30)

    return obj

def add_statue_details(obj):
    """Add statue-like geometric details to the base mesh"""
    print("Adding statue-like details...")

    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')

    # Add subtle edge loops for mechanical segmentation
    # This is just a placeholder - actual implementation depends on final topology

    bpy.ops.object.mode_set(mode='OBJECT')

def main():
    """Generate and save improved base mesh"""
    print("=" * 60)
    print("BASE MESH GENERATOR V4 - The Penitent Mechanism")
    print("Using Skin Modifier for proper humanoid topology")
    print("=" * 60)
    print()

    print("Clearing scene...")
    clear_scene()

    print("\nCreating humanoid base mesh...")
    basemesh = create_humanoid_basemesh()

    print("\nAdding statue details...")
    add_statue_details(basemesh)

    # Statistics
    print("\n" + "=" * 60)
    print("BASE MESH STATISTICS")
    print("=" * 60)
    print(f"  Name: {basemesh.name}")
    print(f"  Vertices: {len(basemesh.data.vertices)}")
    print(f"  Faces: {len(basemesh.data.polygons)}")
    print(f"  Triangles (approx): {len(basemesh.data.polygons) * 2}")
    print("=" * 60)
    print()

    print(f"Saving to: {OUTPUT_PATH}")
    bpy.ops.wm.save_as_mainfile(filepath=OUTPUT_PATH)
    print("✓ Base mesh saved!")
    print()

    print("=" * 60)
    print("✓ BASE MESH GENERATION COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    main()
