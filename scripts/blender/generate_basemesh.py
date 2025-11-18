#!/usr/bin/env python3
"""
Base Mesh Generator for The Penitent Mechanism - V4.0
Professional character topology using Skin Modifier technique

ARCHITECTURE:
- Creates skeletal edge structure (like bones)
- Applies Skin Modifier to generate clean quad topology
- Results in proper humanoid mesh suitable for rigging and deformation
- Kneeling pose baked into the geometry

This approach is used in professional character pipelines and produces
vastly superior topology compared to primitive stacking.
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

def create_skeleton_mesh():
    """
    Create edge-based skeleton that will be converted to mesh via Skin Modifier.
    This is the professional way to generate organic character topology.
    """
    mesh = bpy.data.meshes.new("Skeleton")
    obj = bpy.data.objects.new("Skeleton", mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj

    bm = bmesh.new()

    # Define skeleton points in kneeling pose
    # Format: (name, location, radius_scale)
    skeleton_points = [
        # Spine (bottom to top)
        ('pelvis', Vector((0, 0, 0.50)), 1.2),
        ('spine_low', Vector((0, 0, 0.65)), 1.0),
        ('spine_mid', Vector((0, 0, 0.85)), 0.95),
        ('spine_high', Vector((0, 0, 1.05)), 0.90),
        ('chest', Vector((0, 0, 1.20)), 1.0),

        # Neck and head
        ('neck_base', Vector((0, 0, 1.35)), 0.4),
        ('neck_top', Vector((0, 0, 1.50)), 0.4),
        ('head_base', Vector((0, 0.02, 1.60)), 0.7),
        ('head_top', Vector((0, 0.05, 1.85)), 0.6),

        # Left leg (kneeling)
        ('hip_L', Vector((0.12, 0, 0.50)), 0.5),
        ('knee_L', Vector((0.14, 0.25, 0.30)), 0.35),
        ('ankle_L', Vector((0.14, 0.30, 0.08)), 0.25),
        ('toe_L', Vector((0.14, 0.45, 0.05)), 0.2),

        # Right leg (kneeling)
        ('hip_R', Vector((-0.12, 0, 0.50)), 0.5),
        ('knee_R', Vector((-0.14, 0.25, 0.30)), 0.35),
        ('ankle_R', Vector((-0.14, 0.30, 0.08)), 0.25),
        ('toe_R', Vector((-0.14, 0.45, 0.05)), 0.2),

        # Left arm (prayer-like pose)
        ('shoulder_L', Vector((0.22, 0, 1.20)), 0.35),
        ('elbow_L', Vector((0.32, 0.15, 0.95)), 0.28),
        ('wrist_L', Vector((0.25, 0.35, 0.75)), 0.22),
        ('hand_L', Vector((0.18, 0.45, 0.70)), 0.18),

        # Right arm (prayer-like pose)
        ('shoulder_R', Vector((-0.22, 0, 1.20)), 0.35),
        ('elbow_R', Vector((-0.32, 0.15, 0.95)), 0.28),
        ('wrist_R', Vector((-0.25, 0.35, 0.75)), 0.22),
        ('hand_R', Vector((-0.18, 0.45, 0.70)), 0.18),
    ]

    # Create vertices
    verts = {}
    for name, loc, radius in skeleton_points:
        v = bm.verts.new(loc)
        verts[name] = (v, radius)

    # Create edges (connections) - this defines the skeleton structure
    connections = [
        # Spine chain
        ('pelvis', 'spine_low'),
        ('spine_low', 'spine_mid'),
        ('spine_mid', 'spine_high'),
        ('spine_high', 'chest'),
        ('chest', 'neck_base'),
        ('neck_base', 'neck_top'),
        ('neck_top', 'head_base'),
        ('head_base', 'head_top'),

        # Left leg chain
        ('pelvis', 'hip_L'),
        ('hip_L', 'knee_L'),
        ('knee_L', 'ankle_L'),
        ('ankle_L', 'toe_L'),

        # Right leg chain
        ('pelvis', 'hip_R'),
        ('hip_R', 'knee_R'),
        ('knee_R', 'ankle_R'),
        ('ankle_R', 'toe_R'),

        # Left arm chain
        ('chest', 'shoulder_L'),
        ('shoulder_L', 'elbow_L'),
        ('elbow_L', 'wrist_L'),
        ('wrist_L', 'hand_L'),

        # Right arm chain
        ('chest', 'shoulder_R'),
        ('shoulder_R', 'elbow_R'),
        ('elbow_R', 'wrist_R'),
        ('wrist_R', 'hand_R'),
    ]

    for start_name, end_name in connections:
        start_v = verts[start_name][0]
        end_v = verts[end_name][0]
        bm.edges.new([start_v, end_v])

    bm.to_mesh(mesh)
    bm.free()

    # Apply Skin Modifier - this is the magic that creates proper topology
    skin_mod = obj.modifiers.new(name="Skin", type='SKIN')

    # Set individual vertex radii for proper proportions
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(mesh)

    skin_layer = bm.verts.layers.skin.verify()

    for v in bm.verts:
        # Find matching named vertex
        for name, (vert, radius) in verts.items():
            if v.index == vert.index:
                v[skin_layer].radius = (radius * 0.08, radius * 0.08)
                break

    bmesh.update_edit_mesh(mesh)
    bpy.ops.object.mode_set(mode='OBJECT')

    return obj

def refine_basemesh(obj):
    """
    Apply modifiers and refine the generated mesh.
    """
    print("Applying Skin Modifier...")

    # Apply skin modifier to generate the mesh
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier="Skin")

    # Add Subdivision Surface for smoothness
    print("Adding subdivision surface...")
    subsurf = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 2
    subsurf.subdivision_type = 'CATMULL_CLARK'

    # Apply subdivision to get final topology
    bpy.ops.object.modifier_apply(modifier="Subdivision")

    # Clean up geometry
    print("Cleaning up geometry...")
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=0.001)
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.mesh.delete_loose()
    bpy.ops.object.mode_set(mode='OBJECT')

    # Add one more subdivision modifier (leave unapplied for flexibility)
    final_subsurf = obj.modifiers.new(name="Subdivision_Final", type='SUBSURF')
    final_subsurf.levels = 1
    final_subsurf.render_levels = 2

    # Smooth shading
    bpy.ops.object.shade_smooth()
    obj.data.use_auto_smooth = True
    obj.data.auto_smooth_angle = math.radians(30)

    return obj

def add_facial_features(obj):
    """
    Add minimal facial features for the bronze mask aesthetic.
    Featureless except for almond-shaped eye cutouts.
    """
    print("Adding facial features...")

    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(obj.data)

    # Find head vertices (z > 1.6)
    head_verts = [v for v in bm.verts if v.co.z > 1.6 and v.co.z < 1.80]

    if head_verts:
        # Select front-facing vertices for eyes
        for v in head_verts:
            if v.co.y > 0.05 and abs(v.co.x) > 0.08 and abs(v.co.x) < 0.15:
                # Create slight indentation for eye sockets
                v.co.y += 0.015

    bmesh.update_edit_mesh(obj.data)
    bpy.ops.object.mode_set(mode='OBJECT')

def main():
    """Generate professional-quality base mesh using Skin Modifier"""
    print("=" * 70)
    print("BASE MESH GENERATOR V4.0 - The Penitent Mechanism")
    print("Using professional Skin Modifier technique")
    print("=" * 70)

    print("\n[1/5] Clearing scene...")
    clear_scene()

    print("[2/5] Creating skeleton structure...")
    skeleton = create_skeleton_mesh()
    print(f"  ✓ Created skeleton with {len(skeleton.data.vertices)} control points")

    print("[3/5] Applying Skin Modifier and subdivision...")
    basemesh = refine_basemesh(skeleton)
    print(f"  ✓ Generated mesh with {len(basemesh.data.vertices)} vertices")

    print("[4/5] Adding facial features...")
    add_facial_features(basemesh)

    print("[5/5] Finalizing base mesh...")
    basemesh.name = "PenitentMechanism_Base"

    print(f"\n✓ Base mesh created:")
    print(f"  Name: {basemesh.name}")
    print(f"  Vertices: {len(basemesh.data.vertices)}")
    print(f"  Faces: {len(basemesh.data.polygons)}")
    print(f"  Topology: Clean quads from Skin Modifier")

    print(f"\nSaving to: {OUTPUT_PATH}")
    bpy.ops.wm.save_as_mainfile(filepath=OUTPUT_PATH)
    print("✓ Base mesh saved!")

    print("\n" + "=" * 70)
    print("✓ BASE MESH GENERATION COMPLETE!")
    print("Professional character topology ready for kitbashing.")
    print("=" * 70)

if __name__ == "__main__":
    main()
