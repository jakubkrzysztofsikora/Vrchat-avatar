#!/usr/bin/env python3
"""
Base Mesh Generator for The Penitent Mechanism

Creates a proper humanoid base mesh with good topology in a kneeling pose.
This is saved as a reusable asset that generate_avatar.py will import and modify.

Key principles:
- Proper quad-based topology with edge loops
- Kneeling pose baked into the mesh
- Statue-like aesthetic (geometric, not too organic)
- Optimized for subdivision and modification
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

def create_torso_base():
    """Create torso with proper topology"""
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.9))
    torso = bpy.context.active_object
    torso.name = "Torso"

    # Scale to body proportions
    torso.scale = (0.35, 0.25, 0.5)
    bpy.ops.object.transform_apply(scale=True)

    # Enter edit mode and add subdivision
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=3)

    # Add edge loops for chest/waist definition
    bpy.ops.mesh.loopcut_slide(MESH_OT_loopcut={"number_cuts": 2})

    bpy.ops.object.mode_set(mode='OBJECT')

    # Add subdivision surface modifier
    subsurf = torso.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 3

    return torso

def create_head_neck():
    """Create head and neck as single mesh"""
    # Neck cylinder
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16,
        radius=0.12,
        depth=0.25,
        location=(0, 0, 1.45)
    )
    neck_head = bpy.context.active_object
    neck_head.name = "HeadNeck"

    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(neck_head.data)

    # Extrude top to create head
    top_verts = [v for v in bm.verts if v.co.z > 1.5]
    for v in top_verts:
        v.select = True

    bpy.ops.mesh.extrude_region_move(
        TRANSFORM_OT_translate={"value": (0, 0, 0.3)}
    )

    # Scale head
    bpy.ops.transform.resize(value=(1.8, 1.4, 1.2))

    bmesh.update_edit_mesh(neck_head.data)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Subdivision
    subsurf = neck_head.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 3

    return neck_head

def create_arm(side='L'):
    """Create arm with proper joint topology"""
    sign = 1 if side == 'L' else -1

    # Upper arm
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=12,
        radius=0.08,
        depth=0.35,
        location=(sign * 0.45, 0, 1.15),
        rotation=(0, math.radians(15 * sign), 0)
    )
    arm = bpy.context.active_object
    arm.name = f"Arm_{side}"

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=2)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Forearm
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=12,
        radius=0.07,
        depth=0.30,
        location=(sign * 0.50, 0.15, 0.85),
        rotation=(math.radians(-30), 0, 0)
    )
    forearm = bpy.context.active_object
    forearm.name = f"Forearm_{side}"

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=2)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Hand stub (will be replaced with blade hands later)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8,
        radius=0.06,
        depth=0.15,
        location=(sign * 0.52, 0.35, 0.75),
        rotation=(math.radians(-45), 0, 0)
    )
    hand = bpy.context.active_object
    hand.name = f"Hand_{side}"

    # Join arm parts
    bpy.ops.object.select_all(action='DESELECT')
    arm.select_set(True)
    forearm.select_set(True)
    hand.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.join()

    # Subdivision
    subsurf = arm.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 3

    return arm

def create_leg(side='L'):
    """Create kneeling leg with proper topology"""
    sign = 1 if side == 'L' else -1

    # Thigh (angled for kneeling)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16,
        radius=0.11,
        depth=0.45,
        location=(sign * 0.15, -0.05, 0.70),
        rotation=(math.radians(-60), 0, 0)
    )
    leg = bpy.context.active_object
    leg.name = f"Leg_{side}"

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=3)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Shin (vertical, kneeling)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16,
        radius=0.09,
        depth=0.40,
        location=(sign * 0.15, 0.15, 0.25)
    )
    shin = bpy.context.active_object
    shin.name = f"Shin_{side}"

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=3)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Foot (flat on ground)
    bpy.ops.mesh.primitive_cube_add(
        size=0.18,
        location=(sign * 0.15, 0.22, 0.05)
    )
    foot = bpy.context.active_object
    foot.name = f"Foot_{side}"
    foot.scale = (0.8, 1.5, 0.5)
    bpy.ops.object.transform_apply(scale=True)

    # Join leg parts
    bpy.ops.object.select_all(action='DESELECT')
    leg.select_set(True)
    shin.select_set(True)
    foot.select_set(True)
    bpy.context.view_layer.objects.active = leg
    bpy.ops.object.join()

    # Subdivision
    subsurf = leg.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 3

    return leg

def merge_basemesh(parts):
    """Merge all body parts into single mesh with proper topology"""
    bpy.ops.object.select_all(action='DESELECT')

    for part in parts:
        part.select_set(True)

    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()

    basemesh = bpy.context.active_object
    basemesh.name = "PenitentMechanism_Base"

    # Apply all modifiers
    bpy.ops.object.mode_set(mode='OBJECT')
    for modifier in basemesh.modifiers:
        bpy.ops.object.modifier_apply(modifier=modifier.name)

    # Clean up geometry
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=0.001)
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Final subdivision modifier (leave unapplied for flexibility)
    subsurf = basemesh.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.levels = 1
    subsurf.render_levels = 2

    # Smooth shading
    bpy.ops.object.shade_smooth()
    basemesh.data.use_auto_smooth = True
    basemesh.data.auto_smooth_angle = math.radians(30)

    return basemesh

def main():
    """Generate and save base mesh"""
    print("=" * 60)
    print("BASE MESH GENERATOR - The Penitent Mechanism")
    print("=" * 60)

    print("\nClearing scene...")
    clear_scene()

    print("Creating torso...")
    torso = create_torso_base()

    print("Creating head and neck...")
    head_neck = create_head_neck()

    print("Creating arms...")
    arm_l = create_arm('L')
    arm_r = create_arm('R')

    print("Creating legs (kneeling pose)...")
    leg_l = create_leg('L')
    leg_r = create_leg('R')

    print("\nMerging into single base mesh...")
    parts = [torso, head_neck, arm_l, arm_r, leg_l, leg_r]
    basemesh = merge_basemesh(parts)

    print(f"\n✓ Base mesh created:")
    print(f"  Name: {basemesh.name}")
    print(f"  Vertices: {len(basemesh.data.vertices)}")
    print(f"  Faces: {len(basemesh.data.polygons)}")

    print(f"\nSaving to: {OUTPUT_PATH}")
    bpy.ops.wm.save_as_mainfile(filepath=OUTPUT_PATH)
    print("✓ Base mesh saved!")

    print("\n" + "=" * 60)
    print("✓ BASE MESH GENERATION COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    main()
