#!/usr/bin/env python3
"""
Kitbash Asset Generator for The Penitent Mechanism

Creates high-quality mechanical parts as reusable .blend assets:
- Mechanical Halo (layered bronze rings with details)
- Shoulder Mechanism (gears, plates, pistons)
- Blade Hands (fused blade fingers, L/R variants)
- Cable Clusters (mechanical tendons)

These assets are then imported by generate_avatar_v3.py
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix

OUTPUT_DIR = "Avatar/Kitbash/"

def add_high_quality_modifiers(obj, bevel_width=0.002):
    """Apply AAA hard-surface modifier stack: Bevel + Weighted Normal"""
    # 1. Bevel for edge highlights (critical for realism)
    bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = bevel_width
    bevel.segments = 3
    bevel.limit_method = 'ANGLE'
    bevel.angle_limit = math.radians(30)
    bevel.harden_normals = True

    # 2. Weighted Normal for clean shading on flat surfaces
    wn = obj.modifiers.new(name="WeightedNormal", type='WEIGHTED_NORMAL')
    wn.keep_sharp = True

    obj.data.use_auto_smooth = True
    obj.data.auto_smooth_angle = math.radians(30)

def create_segmented_blade(length=0.25, width=0.03, segments=5):
    """Create a detailed segmented blade (not a primitive cone)"""
    bpy.ops.mesh.primitive_cube_add(size=1)
    blade = bpy.context.active_object
    blade.scale = (width, width/3, length/segments)
    bpy.ops.object.transform_apply(scale=True)

    # Array for segmentation
    array = blade.modifiers.new(name="Array", type='ARRAY')
    array.count = segments
    array.relative_offset_displace = (0, 0, 0.95) # Overlap

    # Taper
    deform = blade.modifiers.new(name="Taper", type='SIMPLE_DEFORM')
    deform.deform_method = 'TAPER'
    deform.factor = 0.85

    return blade

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

def create_halo_ring(radius, thickness, segments=64, name="Ring"):
    """Create a single detailed halo ring with surface detail"""
    bpy.ops.mesh.primitive_torus_add(
        major_radius=radius,
        minor_radius=thickness,
        major_segments=128,  # AAA: High poly count for smooth curves
        minor_segments=16,
        location=(0, 0, 0)
    )
    ring = bpy.context.active_object
    ring.name = name

    add_high_quality_modifiers(ring, thickness * 0.1)

    # Add array of decorative notches
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bm = bmesh.from_edit_mesh(ring.data)

    # Select every Nth edge for detail cuts
    edges = list(bm.edges)
    for i, edge in enumerate(edges):
        if i % 8 == 0:  # Every 8th edge
            edge.select = True

    # Create detail indentations
    if any(e.select for e in bm.edges):
        bpy.ops.mesh.bevel(offset=thickness * 0.05, segments=1)

    bmesh.update_edit_mesh(ring.data)
    bpy.ops.object.mode_set(mode='OBJECT')

    return ring

def create_rune_glyph(index, radius):
    """Create glowing rune glyph decoration"""
    angle = (index / 8.0) * 2 * math.pi
    x = radius * math.cos(angle)
    y = radius * math.sin(angle)

    # Small ico sphere for rune
    bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=2,
        radius=0.015,
        location=(x, y, 0)
    )
    glyph = bpy.context.active_object
    glyph.name = f"Rune_{index}"

    # Add emission material placeholder (will be set in main script)
    return glyph

def generate_mechanical_halo():
    """Generate complete mechanical halo assembly"""
    print("Generating Mechanical Halo...")

    clear_scene()

    # Main outer ring
    ring_outer = create_halo_ring(0.50, 0.012, 64, "Halo_Ring_Outer")
    ring_outer.rotation_euler = (math.radians(10), 0, math.radians(-15))

    # Middle ring with more detail
    ring_mid = create_halo_ring(0.40, 0.015, 48, "Halo_Ring_Mid")
    ring_mid.rotation_euler = (math.radians(15), 0, math.radians(20))

    # Inner ring
    ring_inner = create_halo_ring(0.30, 0.010, 32, "Halo_Ring_Inner")
    ring_inner.rotation_euler = (math.radians(20), 0, math.radians(-30))

    # Add decorative spokes
    for i in range(8):
        angle = (i / 8.0) * 2 * math.pi
        x_outer = 0.30 * math.cos(angle)
        y_outer = 0.30 * math.sin(angle)
        x_inner = 0.18 * math.cos(angle)
        y_inner = 0.18 * math.sin(angle)

        # Create spoke
        bpy.ops.mesh.primitive_cube_add(
            size=0.25,
            location=((x_outer + x_inner)/2, (y_outer + y_inner)/2, 0)
        )
        spoke = bpy.context.active_object
        spoke.name = f"Spoke_{i}"
        spoke.scale = (0.015, 0.08, 0.008)

        # Rotate to align with radial direction
        spoke.rotation_euler = (0, 0, angle + math.radians(90))

        bpy.ops.object.transform_apply(scale=True, rotation=True)

    # Add glowing runes at cardinal points
    runes = []
    for i in range(8):
        glyph = create_rune_glyph(i, 0.40)
        runes.append(glyph)

    # Join all into single object
    bpy.ops.object.select_all(action='SELECT')
    bpy.context.view_layer.objects.active = ring_outer
    bpy.ops.object.join()

    halo = bpy.context.active_object
    halo.name = "Mech_Halo_Assembly"

    # Center pivot
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')

    print(f"  ✓ Created halo: {len(halo.data.vertices)} verts")

    # Save
    filepath = OUTPUT_DIR + "Mech_Halo_01.blend"
    bpy.ops.wm.save_as_mainfile(filepath=filepath)
    print(f"  ✓ Saved: {filepath}")

# ============================================================================
# SHOULDER MECHANISM
# ============================================================================

def create_gear(radius, thickness, teeth=12, name="Gear"):
    """Create detailed gear with proper teeth"""
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=teeth * 4,  # AAA: Higher vertex density
        radius=radius,
        depth=thickness,
        location=(0, 0, 0)
    )
    gear = bpy.context.active_object
    gear.name = name

    # Extrude alternate vertices to create teeth
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(gear.data)

    # Select top rim vertices
    top_verts = [v for v in bm.verts if v.co.z > thickness * 0.4]

    # Select every other vertex for teeth
    for i, v in enumerate(top_verts):
        if i % 2 == 0:
            v.select = True
        else:
            v.select = False

    # Extrude teeth
    if any(v.select for v in top_verts):
        bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value": (0, 0, thickness * 0.2)})
        bpy.ops.transform.resize(value=(1.15, 1.15, 1.0))

    bmesh.update_edit_mesh(gear.data)
    bpy.ops.object.mode_set(mode='OBJECT')

    add_high_quality_modifiers(gear, 0.003)

    return gear

def generate_shoulder_mechanism():
    """Generate complex shoulder armor assembly"""
    print("Generating Shoulder Mechanism...")

    clear_scene()

    # Main shoulder plate with angled bevels
    bpy.ops.mesh.primitive_cube_add(size=0.30, location=(0, 0, 0))
    plate = bpy.context.active_object
    plate.name = "Shoulder_Plate_Main"
    plate.scale = (1.0, 0.9, 0.6)
    bpy.ops.object.transform_apply(scale=True)

    # Chamfer the edges heavily
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.bevel(offset=0.03, segments=3)
    bpy.ops.object.mode_set(mode='OBJECT')

    add_high_quality_modifiers(plate, 0.005)

    # Secondary armor plates
    for i, offset in enumerate([0.12, -0.12, 0.08]):
        bpy.ops.mesh.primitive_cube_add(
            size=0.12,
            location=(0.15, offset, 0.05)
        )
        sub_plate = bpy.context.active_object
        sub_plate.name = f"Armor_Plate_{i}"
        sub_plate.scale = (0.6, 0.8, 0.3)
        sub_plate.rotation_euler = (0, 0, math.radians(15 * i))
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        add_high_quality_modifiers(sub_plate, 0.003)

    # Gears
    gear1 = create_gear(0.08, 0.04, 12, "Gear_Large")
    gear1.location = (0.12, 0.10, 0.10)
    gear1.rotation_euler = (0, math.radians(90), 0)

    gear2 = create_gear(0.05, 0.03, 10, "Gear_Small")
    gear2.location = (0.10, -0.08, 0.08)
    gear2.rotation_euler = (0, math.radians(90), math.radians(25))

    # Pistons/hydraulic cylinders
    for i, (y, z) in enumerate([(0.05, -0.08), (-0.05, -0.06)]):
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=32,  # Higher detail
            radius=0.015,
            depth=0.14,
            location=(0.08, y, z)
        )
        piston = bpy.context.active_object
        piston.name = f"Piston_{i}"
        piston.rotation_euler = (math.radians(90), 0, 0)

        # Piston head
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=32,
            radius=0.022,
            depth=0.035,
            location=(0.08, y + 0.08, z)
        )
        piston_head = bpy.context.active_object
        piston_head.name = f"Piston_Head_{i}"
        piston_head.rotation_euler = (math.radians(90), 0, 0)

    # Rivets/bolts scattered on plates
    for i in range(12):
        x = -0.10 + (i % 4) * 0.06
        y = -0.12 + (i // 4) * 0.08

        bpy.ops.mesh.primitive_cylinder_add(
            vertices=16,  # Higher detail
            radius=0.008,
            depth=0.012,
            location=(x, y, 0.18)
        )
        bolt = bpy.context.active_object
        bolt.name = f"Bolt_{i}"

    # Join all
    bpy.ops.object.select_all(action='SELECT')
    bpy.context.view_layer.objects.active = plate
    bpy.ops.object.join()

    shoulder = bpy.context.active_object
    shoulder.name = "Mech_Shoulder_Assembly"

    # Set origin to attachment point (left side)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

    print(f"  ✓ Created shoulder: {len(shoulder.data.vertices)} verts")

    # Save
    filepath = OUTPUT_DIR + "Mech_Shoulder_01.blend"
    bpy.ops.wm.save_as_mainfile(filepath=filepath)
    print(f"  ✓ Saved: {filepath}")

# ============================================================================
# BLADE HANDS
# ============================================================================

def generate_blade_hand(is_left=True):
    """Generate fused blade-hand"""
    side = "L" if is_left else "R"
    print(f"Generating Blade Hand ({side})...")

    clear_scene()

    # Palm base
    bpy.ops.mesh.primitive_cube_add(size=0.08, location=(0, 0, 0))
    palm = bpy.context.active_object
    palm.name = "Hand_Palm"
    palm.scale = (1.2, 0.6, 0.4)
    bpy.ops.object.transform_apply(scale=True)
    add_high_quality_modifiers(palm, 0.005)

    # Fused blade fingers (3 blades merged together)
    # Use generated segmented blades instead of cones
    for i, x_offset in enumerate([-0.035, 0.0, 0.035]):
        blade = create_segmented_blade(length=0.25, width=0.025, segments=5)
        blade.name = f"Blade_Finger_{i}"

        # Position
        blade.location = (x_offset, 0.08, 0)
        # Rotate forward
        blade.rotation_euler = (math.radians(-15), 0, 0)

        # Apply modifiers to make it real mesh
        bpy.context.view_layer.objects.active = blade
        for mod in blade.modifiers:
            bpy.ops.object.modifier_apply(modifier=mod.name)

        # Sharpen the tip
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles()
        bpy.ops.object.mode_set(mode='OBJECT')

        add_high_quality_modifiers(blade, 0.001)

    # Wrist connector
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,  # Higher detail
        radius=0.04,
        depth=0.06,
        location=(0, -0.05, 0)
    )
    wrist = bpy.context.active_object
    wrist.name = "Wrist_Connector"
    wrist.rotation_euler = (math.radians(90), 0, 0)

    # Decorative armor plates on back of hand
    for i in range(3):
        bpy.ops.mesh.primitive_cube_add(
            size=0.04,
            location=(0, -0.01, 0.01 + i * 0.015)
        )
        plate = bpy.context.active_object
        plate.name = f"Knuckle_Plate_{i}"
        plate.scale = (1.5, 0.3, 0.6)
        bpy.ops.object.transform_apply(scale=True)

    # Join all
    bpy.ops.object.select_all(action='SELECT')
    bpy.context.view_layer.objects.active = palm
    bpy.ops.object.join()

    hand = bpy.context.active_object
    hand.name = f"BladeHand_{side}"

    # Mirror for right hand
    if not is_left:
        hand.scale.x = -1
        bpy.ops.object.transform_apply(scale=True)

    # Set origin to wrist attachment point
    bpy.context.scene.cursor.location = (0, -0.08, 0)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

    print(f"  ✓ Created blade hand: {len(hand.data.vertices)} verts")

    # Save
    filepath = OUTPUT_DIR + f"BladeHand_{side}.blend"
    bpy.ops.wm.save_as_mainfile(filepath=filepath)
    print(f"  ✓ Saved: {filepath}")

# ============================================================================
# CABLE CLUSTERS
# ============================================================================

def create_cable_strand(start, end, radius=0.008, segments=16):
    """Create a single cable using curve"""
    # Calculate control points for bezier curve
    mid = (start + end) / 2
    mid.z -= 0.05  # Sag in middle

    # Create curve
    curve_data = bpy.data.curves.new(name="Cable", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = radius
    curve_data.bevel_resolution = 4

    # Create spline
    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(2)

    # Set points
    spline.bezier_points[0].co = start
    spline.bezier_points[1].co = mid
    spline.bezier_points[2].co = end

    # Set handles for smooth curve
    for point in spline.bezier_points:
        point.handle_left_type = 'AUTO'
        point.handle_right_type = 'AUTO'

    # Create object
    cable_obj = bpy.data.objects.new("Cable_Strand", curve_data)
    bpy.context.collection.objects.link(cable_obj)

    return cable_obj

def generate_cable_cluster():
    """Generate cable cluster for shoulder/back connection"""
    print("Generating Cable Cluster...")

    clear_scene()

    # Shoulder anchor point
    shoulder_pos = Vector((0.35, 0, 0.12))

    # Back anchor points
    back_positions = [
        Vector((0.15, -0.10, 0.08)),
        Vector((0.10, -0.08, 0.05)),
        Vector((0.18, -0.12, 0.10)),
    ]

    cables = []
    for i, back_pos in enumerate(back_positions):
        cable = create_cable_strand(shoulder_pos, back_pos, radius=0.006)
        cable.name = f"Cable_{i}"
        cables.append(cable)

    # Convert curves to mesh
    for cable in cables:
        bpy.ops.object.select_all(action='DESELECT')
        cable.select_set(True)
        bpy.context.view_layer.objects.active = cable
        bpy.ops.object.convert(target='MESH')

    # Add connector nodes at endpoints
    for pos in [shoulder_pos] + back_positions:
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=8,
            ring_count=6,
            radius=0.012,
            location=pos
        )
        node = bpy.context.active_object
        node.name = "Cable_Connector"

    # Join all
    bpy.ops.object.select_all(action='SELECT')
    bpy.context.view_layer.objects.active = cables[0]
    bpy.ops.object.join()

    cluster = bpy.context.active_object
    cluster.name = "Cable_Cluster"

    print(f"  ✓ Created cable cluster: {len(cluster.data.vertices)} verts")

    # Save
    filepath = OUTPUT_DIR + "CableCluster_01.blend"
    bpy.ops.wm.save_as_mainfile(filepath=filepath)
    print(f"  ✓ Saved: {filepath}")

# ============================================================================
# HIGH-FIDELITY ARMOR SET
# ============================================================================

def generate_armor_set():
    """Generate main body armor (Chest, Thighs, Arms) with high detail"""
    print("Generating Armor Set...")
    clear_scene()

    # 1. CHEST PLATE (Cuirass)
    # Start with cylinder segment for curvature, not a cube
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.28, depth=0.35)
    chest = bpy.context.active_object
    chest.name = "Armor_Chest"

    # Sculpt shape: Flatten front/back, widen shoulders
    chest.scale = (1.0, 0.7, 1.0)
    bpy.ops.object.transform_apply(scale=True)

    # Add heavy bevel chamfer
    add_high_quality_modifiers(chest, bevel_width=0.01)

    # Add central ridge detail
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -0.2, 0))
    ridge = bpy.context.active_object
    ridge.scale = (0.08, 0.05, 0.30)
    bpy.ops.object.transform_apply(scale=True)
    add_high_quality_modifiers(ridge, bevel_width=0.005)

    # Join Ridge
    bpy.ops.object.select_all(action='DESELECT')
    ridge.select_set(True)
    chest.select_set(True)
    bpy.context.view_layer.objects.active = chest
    bpy.ops.object.join()

    # 2. THIGH PLATES (Tassets)
    # Curved shield-like plates
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.15, -0.1, -0.4))
    thigh = bpy.context.active_object
    thigh.name = "Armor_Thigh_L"
    thigh.scale = (0.15, 0.05, 0.25)
    bpy.ops.object.transform_apply(scale=True)

    # Bend modifier to curve around leg
    bend = thigh.modifiers.new(name='Bend', type='SIMPLE_DEFORM')
    bend.deform_method = 'BEND'
    bend.angle = math.radians(45)
    bend.deform_axis = 'Z'

    # Apply bend immediately to bake geometry
    bpy.context.view_layer.objects.active = thigh
    bpy.ops.object.modifier_apply(modifier="Bend")
    add_high_quality_modifiers(thigh, bevel_width=0.005)

    # 3. ARM GUARDS (Vambraces)
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.06, depth=0.22)
    arm = bpy.context.active_object
    arm.name = "Armor_Forearm_L"
    arm.location = (0.4, 0, 0)

    # Taper
    taper = arm.modifiers.new(name='Taper', type='SIMPLE_DEFORM')
    taper.deform_method = 'TAPER'
    taper.factor = 0.3
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.modifier_apply(modifier="Taper")
    add_high_quality_modifiers(arm, bevel_width=0.003)

    # 4. SHOULDER PAULDRONS (Replace sphere with layered plates)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=0.12)
    pauldron = bpy.context.active_object
    pauldron.name = "Armor_Pauldron_L"
    pauldron.location = (0.3, 0, 0.3)

    # Cut in half
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.bisect(plane_co=(0,0,0), plane_no=(0,0,1), clear_inner=True)
    bpy.ops.object.mode_set(mode='OBJECT')

    add_high_quality_modifiers(pauldron, bevel_width=0.005)

    # Save Armor Kit
    filepath = OUTPUT_DIR + "Armor_Set_01.blend"
    bpy.ops.wm.save_as_mainfile(filepath=filepath)
    print(f"  ✓ Saved: {filepath}")

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Generate all kitbash assets"""
    print("=" * 70)
    print("KITBASH ASSET GENERATOR - The Penitent Mechanism")
    print("=" * 70)

    assets = [
        ("Mechanical Halo", generate_mechanical_halo),
        ("Shoulder Mechanism", generate_shoulder_mechanism),
        ("Blade Hand (Left)", lambda: generate_blade_hand(True)),
        ("Blade Hand (Right)", lambda: generate_blade_hand(False)),
        ("Cable Cluster", generate_cable_cluster),
        ("High-Res Armor Set", generate_armor_set),
    ]

    for name, func in assets:
        print(f"\n{'='*70}")
        print(f"Creating: {name}")
        print('='*70)
        func()

    print("\n" + "=" * 70)
    print("✓ ALL KITBASH ASSETS GENERATED!")
    print(f"  Assets saved to: {OUTPUT_DIR}")
    print("=" * 70)

if __name__ == "__main__":
    main()
