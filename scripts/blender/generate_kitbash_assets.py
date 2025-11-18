#!/usr/bin/env python3
"""
Kitbash Asset Generator - The Penitent Mechanism
Creates detailed mechanical parts as reusable .blend assets.

These assets are imported by generate_avatar_v3.py instead of being
procedurally generated from primitives each time.
"""

import bpy
import bmesh
import math
import os
from mathutils import Vector

# Output directory
KITBASH_DIR = "Avatar/Kitbash"

def clear_scene():
    """Remove all objects"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)

# ============================================================================
# MECHANICAL HALO
# ============================================================================

def create_mechanical_halo():
    """
    Create a detailed mechanical halo with:
    - Multiple rotating rings
    - Inscribed details
    - Glow points
    - Mechanical greebles
    """
    print("Creating Mechanical Halo...")
    clear_scene()

    collection = bpy.data.collections.new("MechHalo_Collection")
    bpy.context.scene.collection.children.link(collection)

    # Ring 1: Outer ring with inscriptions
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.50,
        minor_radius=0.018,
        major_segments=64,
        minor_segments=16,
        location=(0, 0, 0)
    )
    ring_outer = bpy.context.active_object
    ring_outer.name = "Halo_Ring_Outer"
    collection.objects.link(ring_outer)
    bpy.context.collection.objects.unlink(ring_outer)

    # Add array modifier for inscription detail
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')

    # Ring 2: Middle ring
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.38,
        minor_radius=0.015,
        major_segments=48,
        minor_segments=12,
        location=(0, 0, 0)
    )
    ring_mid = bpy.context.active_object
    ring_mid.name = "Halo_Ring_Mid"
    ring_mid.rotation_euler = (0, 0, math.radians(15))
    collection.objects.link(ring_mid)
    bpy.context.collection.objects.unlink(ring_mid)

    # Ring 3: Inner ring with sharp detail
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.28,
        minor_radius=0.012,
        major_segments=32,
        minor_segments=8,
        location=(0, 0, 0)
    )
    ring_inner = bpy.context.active_object
    ring_inner.name = "Halo_Ring_Inner"
    ring_inner.rotation_euler = (0, 0, math.radians(-20))
    collection.objects.link(ring_inner)
    bpy.context.collection.objects.unlink(ring_inner)

    # Add mechanical connectors between rings
    connector_count = 8
    for i in range(connector_count):
        angle = (i / connector_count) * 2 * math.pi
        x = 0.33 * math.cos(angle)
        y = 0.33 * math.sin(angle)

        bpy.ops.mesh.primitive_cylinder_add(
            vertices=6,
            radius=0.008,
            depth=0.04,
            location=(x, y, 0),
            rotation=(math.radians(90), 0, angle)
        )
        connector = bpy.context.active_object
        connector.name = f"Halo_Connector_{i}"
        collection.objects.link(connector)
        bpy.context.collection.objects.unlink(connector)

    # Add glow spheres
    glow_count = 12
    for i in range(glow_count):
        angle = (i / glow_count) * 2 * math.pi
        radius = 0.42
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)

        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=12,
            ring_count=8,
            radius=0.020,
            location=(x, y, 0)
        )
        glow = bpy.context.active_object
        glow.name = f"Halo_Glow_{i}"
        collection.objects.link(glow)
        bpy.context.collection.objects.unlink(glow)

    # Add mechanical details (greebles)
    for i in range(16):
        angle = (i / 16) * 2 * math.pi + math.radians(11.25)  # Offset
        x = 0.50 * math.cos(angle)
        y = 0.50 * math.sin(angle)

        # Small mechanical box detail
        bpy.ops.mesh.primitive_cube_add(
            size=0.015,
            location=(x, y, 0)
        )
        detail = bpy.context.active_object
        detail.name = f"Halo_Detail_{i}"
        detail.rotation_euler = (0, 0, angle)
        collection.objects.link(detail)
        bpy.context.collection.objects.unlink(detail)

    print(f"  ✓ Created halo with {len(collection.objects)} parts")

    # Save
    output_path = os.path.join(KITBASH_DIR, "Mech_Halo_01.blend")
    bpy.ops.wm.save_as_mainfile(filepath=output_path)
    print(f"  ✓ Saved to: {output_path}")

# ============================================================================
# SHOULDER MECHANISM
# ============================================================================

def create_shoulder_mechanism():
    """
    Create detailed shoulder armor/mechanism with:
    - Main armor plate
    - Gears
    - Pistons
    - Cables
    - Mechanical details
    """
    print("Creating Shoulder Mechanism...")
    clear_scene()

    collection = bpy.data.collections.new("ShoulderMech_Collection")
    bpy.context.scene.collection.children.link(collection)

    # Main shoulder plate
    bpy.ops.mesh.primitive_cube_add(
        size=0.30,
        location=(0, 0, 0)
    )
    plate = bpy.context.active_object
    plate.name = "Shoulder_Plate_Main"
    plate.scale = (1.2, 0.9, 0.7)
    bpy.ops.object.transform_apply(scale=True)

    # Add bevel for mechanical edges
    bevel = plate.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.012
    bevel.segments = 4

    # Add panel lines
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.subdivide(number_cuts=2)
    bpy.ops.object.mode_set(mode='OBJECT')

    collection.objects.link(plate)
    bpy.context.collection.objects.unlink(plate)

    # Large gear 1
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=12,
        radius=0.10,
        depth=0.05,
        location=(0.12, 0, 0.08)
    )
    gear1 = bpy.context.active_object
    gear1.name = "Shoulder_Gear_Large"
    gear1.rotation_euler = (0, math.radians(90), 0)

    # Add gear teeth using array modifier
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(gear1.data)

    # Select outer edge loop and extrude for teeth
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')

    collection.objects.link(gear1)
    bpy.context.collection.objects.unlink(gear1)

    # Small gear 2
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=10,
        radius=0.065,
        depth=0.04,
        location=(-0.08, 0.08, 0.05)
    )
    gear2 = bpy.context.active_object
    gear2.name = "Shoulder_Gear_Small"
    gear2.rotation_euler = (math.radians(15), math.radians(90), 0)
    collection.objects.link(gear2)
    bpy.context.collection.objects.unlink(gear2)

    # Pistons (4x)
    piston_positions = [
        (0.05, -0.10, 0.08),
        (-0.05, -0.10, -0.05),
        (0.08, 0.10, -0.08),
        (-0.10, -0.05, 0.10),
    ]

    for i, pos in enumerate(piston_positions):
        # Piston cylinder
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=8,
            radius=0.018,
            depth=0.15,
            location=pos
        )
        piston = bpy.context.active_object
        piston.name = f"Shoulder_Piston_{i}_Body"
        piston.rotation_euler = (math.radians(90), 0, math.radians(i * 45))
        collection.objects.link(piston)
        bpy.context.collection.objects.unlink(piston)

        # Piston head
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=8,
            radius=0.025,
            depth=0.035,
            location=(pos[0], pos[1] - 0.08, pos[2])
        )
        piston_head = bpy.context.active_object
        piston_head.name = f"Shoulder_Piston_{i}_Head"
        piston_head.rotation_euler = (math.radians(90), 0, 0)
        collection.objects.link(piston_head)
        bpy.context.collection.objects.unlink(piston_head)

    # Cable mounts (connection points for cables)
    for i in range(6):
        angle = (i / 6) * math.pi  # Half circle
        x = 0.15 * math.cos(angle)
        z = 0.15 * math.sin(angle) - 0.05

        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.015,
            minor_radius=0.005,
            location=(x, -0.12, z)
        )
        mount = bpy.context.active_object
        mount.name = f"Shoulder_CableMount_{i}"
        mount.rotation_euler = (0, math.radians(90), 0)
        collection.objects.link(mount)
        bpy.context.collection.objects.unlink(mount)

    # Armor plates (layered)
    for i in range(3):
        offset = i * 0.04
        bpy.ops.mesh.primitive_cube_add(
            size=0.12 - offset * 0.3,
            location=(0.08 - offset * 0.3, -0.10 - offset * 0.02, -0.08)
        )
        armor = bpy.context.active_object
        armor.name = f"Shoulder_ArmorPlate_{i}"
        armor.scale = (1.3, 0.3, 0.8)
        bpy.ops.object.transform_apply(scale=True)

        bevel = armor.modifiers.new(name="Bevel", type='BEVEL')
        bevel.width = 0.008
        bevel.segments = 3

        collection.objects.link(armor)
        bpy.context.collection.objects.unlink(armor)

    print(f"  ✓ Created shoulder mechanism with {len(collection.objects)} parts")

    # Save
    output_path = os.path.join(KITBASH_DIR, "Mech_Shoulder_01.blend")
    bpy.ops.wm.save_as_mainfile(filepath=output_path)
    print(f"  ✓ Saved to: {output_path}")

# ============================================================================
# BLADE HAND
# ============================================================================

def create_blade_hand():
    """
    Create fused blade-hand with:
    - Mechanical palm
    - Fused blade fingers
    - Mechanical joints
    - Sharp edges
    """
    print("Creating Blade Hand...")
    clear_scene()

    collection = bpy.data.collections.new("BladeHand_Collection")
    bpy.context.scene.collection.children.link(collection)

    # Palm base
    bpy.ops.mesh.primitive_cube_add(
        size=0.08,
        location=(0, 0, 0)
    )
    palm = bpy.context.active_object
    palm.name = "BladeHand_Palm"
    palm.scale = (1.0, 0.6, 0.4)
    bpy.ops.object.transform_apply(scale=True)

    bevel = palm.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.006
    bevel.segments = 3

    collection.objects.link(palm)
    bpy.context.collection.objects.unlink(palm)

    # Main blade (fused fingers)
    bpy.ops.mesh.primitive_cone_add(
        vertices=6,
        radius1=0.055,
        radius2=0.008,
        depth=0.28,
        location=(0, 0, 0.16)
    )
    blade_main = bpy.context.active_object
    blade_main.name = "BladeHand_MainBlade"
    blade_main.rotation_euler = (math.radians(10), 0, 0)

    # Add sharp edges
    bevel = blade_main.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.003
    bevel.segments = 2
    bevel.limit_method = 'ANGLE'
    bevel.angle_limit = math.radians(40)

    collection.objects.link(blade_main)
    bpy.context.collection.objects.unlink(blade_main)

    # Side blade 1 (thumb blade)
    bpy.ops.mesh.primitive_cone_add(
        vertices=5,
        radius1=0.030,
        radius2=0.005,
        depth=0.15,
        location=(0.045, -0.02, 0.10)
    )
    blade_thumb = bpy.context.active_object
    blade_thumb.name = "BladeHand_ThumbBlade"
    blade_thumb.rotation_euler = (math.radians(-20), 0, math.radians(45))

    bevel = blade_thumb.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.002
    bevel.segments = 2

    collection.objects.link(blade_thumb)
    bpy.context.collection.objects.unlink(blade_thumb)

    # Mechanical joint details
    for i in range(3):
        z = 0.05 + i * 0.04

        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.045 - i * 0.008,
            minor_radius=0.006,
            major_segments=24,
            minor_segments=8,
            location=(0, 0, z)
        )
        joint = bpy.context.active_object
        joint.name = f"BladeHand_Joint_{i}"
        collection.objects.link(joint)
        bpy.context.collection.objects.unlink(joint)

    # Pistons on palm
    for i in range(4):
        angle = (i / 4) * math.pi - math.radians(45)
        x = 0.035 * math.cos(angle)
        y = 0.025 * math.sin(angle)

        bpy.ops.mesh.primitive_cylinder_add(
            vertices=6,
            radius=0.005,
            depth=0.04,
            location=(x, y, 0.02)
        )
        piston = bpy.context.active_object
        piston.name = f"BladeHand_Piston_{i}"
        collection.objects.link(piston)
        bpy.context.collection.objects.unlink(piston)

    # Wrist connection ring
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16,
        radius=0.042,
        depth=0.025,
        location=(0, 0, -0.04)
    )
    wrist = bpy.context.active_object
    wrist.name = "BladeHand_WristConnector"
    collection.objects.link(wrist)
    bpy.context.collection.objects.unlink(wrist)

    print(f"  ✓ Created blade hand with {len(collection.objects)} parts")

    # Save
    output_path = os.path.join(KITBASH_DIR, "BladeHand_01.blend")
    bpy.ops.wm.save_as_mainfile(filepath=output_path)
    print(f"  ✓ Saved to: {output_path}")

# ============================================================================
# CABLE CLUSTER
# ============================================================================

def create_cable_cluster():
    """
    Create cable cluster for connecting mechanical parts.
    Uses curve objects converted to mesh.
    """
    print("Creating Cable Cluster...")
    clear_scene()

    collection = bpy.data.collections.new("CableCluster_Collection")
    bpy.context.scene.collection.children.link(collection)

    # Create several cables with different paths
    cable_count = 6

    for i in range(cable_count):
        # Create bezier curve
        curve_data = bpy.data.curves.new(name=f"Cable_{i}_Curve", type='CURVE')
        curve_data.dimensions = '3D'
        curve_data.fill_mode = 'FULL'
        curve_data.bevel_depth = 0.008 - i * 0.001  # Varying thickness

        # Create spline
        spline = curve_data.splines.new('BEZIER')
        spline.bezier_points.add(2)  # Add 2 more points (total 3)

        # Define cable path (example: shoulder to back)
        points = [
            Vector((0, 0, 0)),  # Start
            Vector((0.05 + i * 0.02, 0.08, 0.15)),  # Mid
            Vector((0.15, 0.20, 0.25)),  # End
        ]

        for j, point in enumerate(points):
            spline.bezier_points[j].co = point
            spline.bezier_points[j].handle_left_type = 'AUTO'
            spline.bezier_points[j].handle_right_type = 'AUTO'

        # Create object
        cable_obj = bpy.data.objects.new(f"Cable_{i}", curve_data)
        collection.objects.link(cable_obj)

    # Add connector nodes at cable ends
    for i in range(4):
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=8,
            ring_count=6,
            radius=0.012,
            location=(i * 0.05, i * 0.07, i * 0.08)
        )
        node = bpy.context.active_object
        node.name = f"Cable_Node_{i}"
        collection.objects.link(node)
        bpy.context.collection.objects.unlink(node)

    print(f"  ✓ Created cable cluster with {len(collection.objects)} parts")

    # Save
    output_path = os.path.join(KITBASH_DIR, "CableCluster_01.blend")
    bpy.ops.wm.save_as_mainfile(filepath=output_path)
    print(f"  ✓ Saved to: {output_path}")

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Generate all kitbash assets"""
    print("=" * 60)
    print("KITBASH ASSET GENERATOR - The Penitent Mechanism")
    print("=" * 60)
    print()

    # Ensure output directory exists
    os.makedirs(KITBASH_DIR, exist_ok=True)

    # Generate each asset
    create_mechanical_halo()
    print()

    create_shoulder_mechanism()
    print()

    create_blade_hand()
    print()

    create_cable_cluster()
    print()

    print("=" * 60)
    print("✓ ALL KITBASH ASSETS GENERATED!")
    print("=" * 60)
    print(f"\nAssets saved to: {KITBASH_DIR}/")
    print("  - Mech_Halo_01.blend")
    print("  - Mech_Shoulder_01.blend")
    print("  - BladeHand_01.blend")
    print("  - CableCluster_01.blend")
    print()

if __name__ == "__main__":
    main()
