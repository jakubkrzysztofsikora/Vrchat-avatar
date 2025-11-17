#!/usr/bin/env python3
"""
The Penitent Mechanism - Procedural VRChat Avatar Generator
Generates a horror avatar: Buddhist/Shinto statue possessed by Dwemer machinery.

Concept: Kneeling shrine guardian - faith corrupted by technology.
Asian minimalist horror + Elder Scrolls (Dwemer) + Lovecraftian wrongness.
"""

import bpy
import bmesh
import math
import mathutils
import random
import addon_utils
from mathutils import Vector, Matrix

# Configuration
AVATAR_HEIGHT = 2.1  # Standing height (kneeling default is ~1.4m)
KNEELING = True  # Default pose
SEED = 42
random.seed(SEED)

def enable_rigify():
    """Enable Rigify addon"""
    print("Enabling Rigify addon...")
    addon_utils.enable("rigify", default_set=True, persistent=True)

    if "rigify" in bpy.context.preferences.addons:
        print("✓ Rigify enabled successfully!")
        return True
    else:
        print("⚠ WARNING: Rigify could not be enabled!")
        return False

def clear_scene():
    """Remove default objects"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    print("✓ Scene cleared")

# ============================================================================
# ARMATURE CREATION (Preserved from original, with extensions)
# ============================================================================

def create_extended_humanoid_armature():
    """Create humanoid armature with extra bones for telescoping and mechanisms"""
    print("Creating extended humanoid armature...")

    # Try Rigify first
    rigify_enabled = enable_rigify()

    if rigify_enabled:
        try:
            bpy.ops.object.armature_basic_human_metarig_add()
            metarig = bpy.context.active_object
            metarig.name = "Penitent_MetaRig"
            metarig.scale = (1.0, 1.0, AVATAR_HEIGHT / 1.7)
            bpy.ops.object.transform_apply(scale=True)
            print("✓ Rigify meta-rig created")
            return metarig
        except Exception as e:
            print(f"⚠ Rigify failed: {e}, using manual armature")

    # Fallback: Manual armature
    return create_manual_extended_armature()

def create_manual_extended_armature():
    """Create manual armature with extra bones for mechanisms"""
    print("Creating manual extended armature...")

    bpy.ops.object.armature_add(location=(0, 0, 0))
    armature = bpy.context.active_object
    armature.name = "Penitent_Rig"
    armature.show_in_front = True

    bpy.ops.object.mode_set(mode='EDIT')
    arm_data = armature.data
    bones = arm_data.edit_bones
    bones.clear()

    def add_bone(name, head, tail, parent=None):
        bone = bones.new(name)
        bone.head = head
        bone.tail = tail
        if parent:
            bone.parent = bones[parent]
        return bone

    scale = AVATAR_HEIGHT / 1.7

    # Core spine
    add_bone("Hips", (0, 0, 0.9 * scale), (0, 0, 1.0 * scale))
    add_bone("Spine", (0, 0, 1.0 * scale), (0, 0, 1.2 * scale), "Hips")
    add_bone("Spine.001", (0, 0, 1.2 * scale), (0, 0, 1.4 * scale), "Spine")
    add_bone("Chest", (0, 0, 1.4 * scale), (0, 0, 1.6 * scale), "Spine.001")

    # Extended neck (4 segments for telescoping)
    neck_base_z = 1.6 * scale
    neck_seg_len = 0.05 * scale
    add_bone("Neck_Base", (0, 0, neck_base_z), (0, 0, neck_base_z + neck_seg_len), "Chest")
    add_bone("Neck_Mid1", (0, 0, neck_base_z + neck_seg_len),
             (0, 0, neck_base_z + neck_seg_len * 2), "Neck_Base")
    add_bone("Neck_Mid2", (0, 0, neck_base_z + neck_seg_len * 2),
             (0, 0, neck_base_z + neck_seg_len * 3), "Neck_Mid1")
    add_bone("Neck_Top", (0, 0, neck_base_z + neck_seg_len * 3),
             (0, 0, neck_base_z + neck_seg_len * 4), "Neck_Mid2")
    add_bone("Head", (0, 0, neck_base_z + neck_seg_len * 4),
             (0, 0, neck_base_z + neck_seg_len * 4 + 0.15 * scale), "Neck_Top")

    # Arms (standard humanoid)
    # Left arm (organic)
    add_bone("Shoulder.L", (0.05 * scale, 0, 1.55 * scale), (0.15 * scale, 0, 1.5 * scale), "Chest")
    add_bone("UpperArm.L", (0.15 * scale, 0, 1.5 * scale), (0.35 * scale, 0, 1.2 * scale), "Shoulder.L")
    add_bone("LowerArm.L", (0.35 * scale, 0, 1.2 * scale), (0.55 * scale, 0, 0.95 * scale), "UpperArm.L")
    add_bone("Hand.L", (0.55 * scale, 0, 0.95 * scale), (0.65 * scale, 0, 0.88 * scale), "LowerArm.L")

    # Right arm (mechanical - will have extra bones for segments)
    add_bone("Shoulder.R", (-0.05 * scale, 0, 1.55 * scale), (-0.15 * scale, 0, 1.5 * scale), "Chest")
    add_bone("UpperArm.R", (-0.15 * scale, 0, 1.5 * scale), (-0.35 * scale, 0, 1.2 * scale), "Shoulder.R")
    add_bone("LowerArm.R", (-0.35 * scale, 0, 1.2 * scale), (-0.55 * scale, 0, 0.95 * scale), "UpperArm.R")
    add_bone("Hand.R", (-0.55 * scale, 0, 0.95 * scale), (-0.65 * scale, 0, 0.88 * scale), "LowerArm.R")

    # Legs with telescoping segments
    # Left leg
    add_bone("UpperLeg.L", (0.1 * scale, 0, 0.9 * scale), (0.1 * scale, 0, 0.5 * scale), "Hips")
    add_bone("LowerLeg.L_Seg1", (0.1 * scale, 0, 0.5 * scale), (0.1 * scale, 0, 0.3 * scale), "UpperLeg.L")
    add_bone("LowerLeg.L_Seg2", (0.1 * scale, 0, 0.3 * scale), (0.1 * scale, 0, 0.1 * scale), "LowerLeg.L_Seg1")
    add_bone("Foot.L", (0.1 * scale, 0, 0.1 * scale), (0.1 * scale, 0.1 * scale, 0.02 * scale), "LowerLeg.L_Seg2")
    add_bone("Toes.L", (0.1 * scale, 0.1 * scale, 0.02 * scale), (0.1 * scale, 0.18 * scale, 0.02 * scale), "Foot.L")

    # Right leg
    add_bone("UpperLeg.R", (-0.1 * scale, 0, 0.9 * scale), (-0.1 * scale, 0, 0.5 * scale), "Hips")
    add_bone("LowerLeg.R_Seg1", (-0.1 * scale, 0, 0.5 * scale), (-0.1 * scale, 0, 0.3 * scale), "UpperLeg.R")
    add_bone("LowerLeg.R_Seg2", (-0.1 * scale, 0, 0.3 * scale), (-0.1 * scale, 0, 0.1 * scale), "LowerLeg.R_Seg1")
    add_bone("Foot.R", (-0.1 * scale, 0, 0.1 * scale), (-0.1 * scale, 0.1 * scale, 0.02 * scale), "LowerLeg.R_Seg2")
    add_bone("Toes.R", (-0.1 * scale, 0.1 * scale, 0.02 * scale), (-0.1 * scale, 0.18 * scale, 0.02 * scale), "Foot.R")

    bpy.ops.object.mode_set(mode='OBJECT')

    print(f"✓ Manual armature created with {len(bones)} bones")
    return armature

# ============================================================================
# MESH CREATION - The Penitent Mechanism Design
# ============================================================================

def create_body_statue(scale):
    """Create main body mesh - ascetic, segmented statue construction"""
    print("  Creating statue body...")

    # Upper torso - simple cylinder, NOT muscular
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.14 * scale,
        depth=0.4 * scale,
        location=(0, 0, 1.35 * scale),
        vertices=16
    )
    chest = bpy.context.active_object
    chest.name = "Body_Chest"

    # Edit to create angular, geometric form
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(chest.data)

    for v in bm.verts:
        z_pos = v.co.z
        # Narrower waist
        if z_pos < -0.15 * scale:
            v.co.x *= 0.75
            v.co.y *= 0.75
        # Narrow shoulders (ascetic)
        elif z_pos > 0.1 * scale:
            v.co.x *= 0.9
            v.co.y *= 0.9

        # Add center seam line (BJD construction)
        if abs(v.co.x) < 0.01 * scale:
            v.co.x *= 1.02  # Slight ridge

    bmesh.update_edit_mesh(chest.data)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Lower torso / pelvis
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.13 * scale,
        depth=0.25 * scale,
        location=(0, 0, 1.05 * scale),
        vertices=16
    )
    pelvis = bpy.context.active_object
    pelvis.name = "Body_Pelvis"

    # Add horizontal segment lines (rib segments)
    chest.modifiers.new(name="Solidify", type='SOLIDIFY')

    # Join torso pieces
    bpy.ops.object.select_all(action='DESELECT')
    chest.select_set(True)
    pelvis.select_set(True)
    bpy.context.view_layer.objects.active = chest
    bpy.ops.object.join()

    body = bpy.context.active_object
    body.name = "Body"

    # Smooth but keep geometric feel
    bpy.ops.object.shade_smooth()

    # Add subtle subdivision
    subdiv = body.modifiers.new(name="Subdiv", type='SUBSURF')
    subdiv.levels = 1
    subdiv.render_levels = 1

    print(f"    Body: {len(body.data.vertices)} vertices (statue construction)")
    return body

def create_segmented_neck(scale):
    """Create 4-segment bronze collar neck with ivory flesh between"""
    print("  Creating segmented neck...")

    neck_parts = []
    base_z = 1.6 * scale
    segment_height = 0.03 * scale
    gap = 0.02 * scale

    for i in range(4):
        z_pos = base_z + i * (segment_height + gap) + segment_height / 2

        # Bronze collar ring
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.055 * scale,
            minor_radius=0.008 * scale,
            location=(0, 0, z_pos),
            major_segments=24,
            minor_segments=8
        )
        collar = bpy.context.active_object
        collar.name = f"Neck_Collar_{i}"
        neck_parts.append(collar)

        # Ivory flesh segment between collars (except last)
        if i < 3:
            bpy.ops.mesh.primitive_cylinder_add(
                radius=0.048 * scale,
                depth=gap,
                location=(0, 0, z_pos + segment_height / 2 + gap / 2),
                vertices=16
            )
            flesh = bpy.context.active_object
            flesh.name = f"Neck_Flesh_{i}"
            neck_parts.append(flesh)

    # Join all neck parts
    bpy.ops.object.select_all(action='DESELECT')
    for part in neck_parts:
        part.select_set(True)
    bpy.context.view_layer.objects.active = neck_parts[0]
    bpy.ops.object.join()

    neck = bpy.context.active_object
    neck.name = "Neck_Segmented"
    bpy.ops.object.shade_smooth()

    print(f"    Neck: 4 segments, {len(neck.data.vertices)} vertices")
    return neck

def create_bronze_mask_face(scale):
    """Create smooth bronze mask with almond eyes, NO nose/mouth"""
    print("  Creating bronze mask face...")

    # Base mask - half sphere (front face only)
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.11 * scale,
        location=(0, -0.08 * scale, 1.88 * scale),
        segments=32,
        ring_count=24
    )
    mask = bpy.context.active_object
    mask.name = "Face_Mask"

    # Scale to elongated oval
    mask.scale = (0.85, 0.9, 1.1)
    bpy.ops.object.transform_apply(scale=True)

    # Delete back half (only front mask)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.bisect(plane_co=(0, 0, 0), plane_no=(0, 1, 0), clear_outer=True)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Create eye cutouts
    eye_left = create_eye_cutout(scale, -0.048, 1.885)
    eye_right = create_eye_cutout(scale, 0.048, 1.885)

    # Boolean subtract eyes from mask
    bool_left = mask.modifiers.new(name="EyeL_Bool", type='BOOLEAN')
    bool_left.operation = 'DIFFERENCE'
    bool_left.object = eye_left

    bool_right = mask.modifiers.new(name="EyeR_Bool", type='BOOLEAN')
    bool_right.operation = 'DIFFERENCE'
    bool_right.object = eye_right

    # Apply booleans
    bpy.context.view_layer.objects.active = mask
    bpy.ops.object.modifier_apply(modifier="EyeL_Bool")
    bpy.ops.object.modifier_apply(modifier="EyeR_Bool")

    # Delete boolean objects
    bpy.data.objects.remove(eye_left, do_unlink=True)
    bpy.data.objects.remove(eye_right, do_unlink=True)

    # Add edge split to keep eye edges sharp
    edge_split = mask.modifiers.new(name="EdgeSplit", type='EDGE_SPLIT')
    edge_split.split_angle = math.radians(30)

    # Smooth rest of mask
    subdiv = mask.modifiers.new(name="Subdiv", type='SUBSURF')
    subdiv.levels = 2
    subdiv.render_levels = 2

    bpy.ops.object.shade_smooth()

    print(f"    Mask: {len(mask.data.vertices)} vertices (smooth bronze)")
    return mask

def create_eye_cutout(scale, x_offset, z_pos):
    """Create almond-shaped eye cutout"""
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.025 * scale,
        location=(x_offset, -0.15 * scale, z_pos),
        segments=16,
        ring_count=12
    )
    eye = bpy.context.active_object
    eye.scale = (0.8, 1.0, 0.6)  # Almond shape
    bpy.ops.object.transform_apply(scale=True)
    return eye

def create_eye_glow(scale, x_offset, z_pos, side):
    """Create emissive amber glow inside eye socket"""
    bpy.ops.mesh.primitive_plane_add(
        size=0.04 * scale,
        location=(x_offset, -0.145 * scale, z_pos)
    )
    glow = bpy.context.active_object
    glow.name = f"Eye_Glow_{side}"
    glow.scale = (0.8, 0.6, 1.0)  # Almond shape
    bpy.ops.object.transform_apply(scale=True)
    glow.rotation_euler = (0, math.radians(90), 0)  # Face forward
    bpy.ops.object.transform_apply(rotation=True)
    return glow

def create_ivory_hair_with_cables(scale):
    """Create carved ivory hair transitioning to bronze cables"""
    print("  Creating hair with cable transition...")

    hair_objects = []
    num_strands = 24

    for i in range(num_strands):
        # Distribute around head
        angle = (i / num_strands) * 2 * math.pi
        radius = 0.09 * scale

        x = math.cos(angle) * radius
        y_base = math.sin(angle) * radius - 0.05 * scale  # Offset back

        # Create hair card (plane with alpha)
        curve_data = bpy.data.curves.new(name=f"Hair_{i}", type='CURVE')
        curve_data.dimensions = '3D'
        curve_data.fill_mode = 'FULL'

        # Taper: wide at top (hair) to thin at bottom (cable)
        if i < 16:  # Front/side hair
            curve_data.bevel_depth = 0.012 * scale
        else:  # Back cables
            curve_data.bevel_depth = 0.004 * scale

        curve_data.bevel_resolution = 2
        curve_data.use_fill_caps = True

        # Create spline
        spline = curve_data.splines.new('BEZIER')
        spline.bezier_points.add(3)  # 4 points total

        # Points: head to mid-back
        points = [
            (x, y_base, 1.92 * scale),  # Scalp
            (x * 1.1, y_base * 1.2 - 0.05 * scale, 1.75 * scale),  # Upper back
            (x * 0.95, y_base * 1.1 - 0.15 * scale, 1.45 * scale),  # Mid back (transition)
            (x * 0.8, y_base * 0.9 - 0.25 * scale, 1.15 * scale),  # Lower back (cable)
        ]

        for idx, pos in enumerate(points):
            point = spline.bezier_points[idx]
            point.co = pos
            point.handle_left_type = 'AUTO'
            point.handle_right_type = 'AUTO'

        # Create object
        hair_obj = bpy.data.objects.new(f"Hair_{i}", curve_data)
        bpy.context.collection.objects.link(hair_obj)
        hair_objects.append(hair_obj)

    print(f"    Hair: {len(hair_objects)} strands/cables")
    return hair_objects

def create_fused_hand(scale, side):
    """Create hand with fingers fused into single blade-point"""
    print(f"  Creating fused blade-hand ({side})...")

    side_mult = 1 if side == 'L' else -1
    x_pos = 0.65 * scale * side_mult
    y_pos = 0
    z_pos = 0.88 * scale

    # Create blade shape - tapered from wrist to tip
    bpy.ops.mesh.primitive_cube_add(
        size=0.1 * scale,
        location=(x_pos, y_pos, z_pos)
    )
    hand = bpy.context.active_object
    hand.name = f"Hand_Fused_{side}"

    # Scale to blade shape
    hand.scale = (0.4, 0.2, 2.0)
    bpy.ops.object.transform_apply(scale=True)

    # Edit to create finger grooves and taper
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(hand.data)

    for v in bm.verts:
        local_z = v.co.z - z_pos

        # Taper to point
        if local_z < 0:  # Tip end
            taper_factor = abs(local_z) / (0.2 * scale)
            v.co.x *= (1.0 - taper_factor * 0.7)
            v.co.y *= (1.0 - taper_factor * 0.8)

        # Add finger grooves (4 shallow channels)
        x_local = (v.co.x - x_pos) / (0.04 * scale)
        if abs(x_local) < 2.0:
            groove = abs(x_local % 0.5 - 0.25)  # Repeating groove
            v.co.y -= groove * 0.002 * scale

    bmesh.update_edit_mesh(hand.data)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Add wrist ball joint
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.03 * scale,
        location=(x_pos, y_pos, z_pos + 0.05 * scale),
        segments=16,
        ring_count=12
    )
    wrist = bpy.context.active_object
    wrist.name = f"Hand_Wrist_{side}"

    # Join hand and wrist
    bpy.ops.object.select_all(action='DESELECT')
    hand.select_set(True)
    wrist.select_set(True)
    bpy.context.view_layer.objects.active = hand
    bpy.ops.object.join()

    hand = bpy.context.active_object
    bpy.ops.object.shade_smooth()

    print(f"    Hand ({side}): Fused blade, {len(hand.data.vertices)} vertices")
    return hand

def create_arm_segment(scale, side, is_bronze=False):
    """Create arm (left=ivory smooth, right=bronze segmented)"""
    side_mult = 1 if side == 'L' else -1
    print(f"  Creating {'bronze segmented' if is_bronze else 'ivory smooth'} arm ({side})...")

    parts = []

    # Shoulder joint
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.07 * scale,
        location=(0.15 * scale * side_mult, 0, 1.5 * scale),
        segments=16,
        ring_count=12
    )
    shoulder = bpy.context.active_object
    shoulder.name = f"Arm_Shoulder_{side}"
    parts.append(shoulder)

    if is_bronze:
        # Right arm: Segmented bronze cylinders
        seg_positions = [
            (0.23 * scale, 1.38 * scale),  # Upper arm segment 1
            (0.30 * scale, 1.26 * scale),  # Upper arm segment 2
            (0.37 * scale, 1.14 * scale),  # Upper arm segment 3
            (0.44 * scale, 1.05 * scale),  # Forearm segment 1
            (0.51 * scale, 0.98 * scale),  # Forearm segment 2
        ]

        for idx, (x, z) in enumerate(seg_positions):
            bpy.ops.mesh.primitive_cylinder_add(
                radius=0.04 * scale * (1.0 - idx * 0.05),  # Slight taper
                depth=0.09 * scale,
                location=(x * side_mult, 0, z),
                vertices=12
            )
            seg = bpy.context.active_object
            seg.name = f"Arm_Segment_{side}_{idx}"

            # Add gear teeth decorative ring
            torus = create_gear_ring(scale, x * side_mult, z - 0.045 * scale, 0.04 * scale)
            parts.extend([seg, torus])
    else:
        # Left arm: Smooth ivory (single piece upper + forearm)
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.045 * scale,
            depth=0.28 * scale,
            location=(0.27 * scale * side_mult, 0, 1.32 * scale),
            vertices=16
        )
        upper_arm = bpy.context.active_object
        upper_arm.name = f"Arm_Upper_{side}"
        parts.append(upper_arm)

        # Elbow
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.05 * scale,
            location=(0.38 * scale * side_mult, 0, 1.2 * scale),
            segments=16,
            ring_count=12
        )
        elbow = bpy.context.active_object
        elbow.name = f"Arm_Elbow_{side}"
        parts.append(elbow)

        # Forearm
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.04 * scale,
            depth=0.25 * scale,
            location=(0.48 * scale * side_mult, 0, 1.0 * scale),
            vertices=16
        )
        forearm = bpy.context.active_object
        forearm.name = f"Arm_Forearm_{side}"
        parts.append(forearm)

    # Join arm parts
    bpy.ops.object.select_all(action='DESELECT')
    for part in parts:
        part.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()

    arm = bpy.context.active_object
    arm.name = f"Arm_{side}"
    bpy.ops.object.shade_smooth()

    return arm

def create_gear_ring(scale, x, z, radius):
    """Create decorative gear ring for joints"""
    bpy.ops.mesh.primitive_torus_add(
        major_radius=radius,
        minor_radius=0.003 * scale,
        location=(x, 0, z),
        major_segments=20,
        minor_segments=6
    )
    ring = bpy.context.active_object
    return ring

def create_shoulder_mechanism(scale):
    """Create rotating gear mechanism on right shoulder"""
    print("  Creating shoulder mechanism...")

    x_pos = -0.15 * scale
    z_pos = 1.55 * scale

    gears = []

    # Three concentric gear rings
    gear_sizes = [
        (0.08 * scale, "Outer"),
        (0.06 * scale, "Mid"),
        (0.04 * scale, "Inner"),
    ]

    for radius, name in gear_sizes:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=radius,
            depth=0.02 * scale,
            location=(x_pos, 0, z_pos),
            vertices=30
        )
        gear = bpy.context.active_object
        gear.name = f"Shoulder_Gear_{name}"

        # Add gear teeth with array modifier
        bpy.ops.mesh.primitive_cube_add(
            size=0.01 * scale,
            location=(x_pos + radius, 0, z_pos)
        )
        tooth = bpy.context.active_object

        array_mod = tooth.modifiers.new(name="Array", type='ARRAY')
        array_mod.use_relative_offset = False
        array_mod.use_object_offset = True

        # Create empty for rotation
        bpy.ops.object.empty_add(location=(x_pos, 0, z_pos))
        empty = bpy.context.active_object
        empty.rotation_euler = (0, 0, 2 * math.pi / 20)
        array_mod.offset_object = empty
        array_mod.count = 20

        # Join teeth to gear
        bpy.ops.object.select_all(action='DESELECT')
        gear.select_set(True)
        tooth.select_set(True)
        bpy.context.view_layer.objects.active = gear
        bpy.ops.object.join()

        gears.append(gear)

        # Offset each ring slightly
        z_pos += 0.015 * scale

    # Join all gears
    bpy.ops.object.select_all(action='DESELECT')
    for gear in gears:
        gear.select_set(True)
    bpy.context.view_layer.objects.active = gears[0]
    bpy.ops.object.join()

    mechanism = bpy.context.active_object
    mechanism.name = "ShoulderMechanism_Right"

    print(f"    Mechanism: 3 gears, {len(mechanism.data.vertices)} vertices")
    return mechanism

def create_telescoping_legs(scale, side):
    """Create legs with telescoping segments (compressed in kneeling pose)"""
    side_mult = 1 if side == 'L' else -1
    print(f"  Creating telescoping leg ({side})...")

    parts = []

    # Hip joint
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.07 * scale,
        location=(0.1 * scale * side_mult, 0, 0.85 * scale),
        segments=16,
        ring_count=12
    )
    hip = bpy.context.active_object
    hip.name = f"Leg_Hip_{side}"
    parts.append(hip)

    # Thigh
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.06 * scale,
        depth=0.35 * scale,
        location=(0.1 * scale * side_mult, 0, 0.65 * scale),
        vertices=16
    )
    thigh = bpy.context.active_object
    thigh.name = f"Leg_Thigh_{side}"
    parts.append(thigh)

    # Lower leg segment 1 (outer cylinder)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.05 * scale,
        depth=0.20 * scale,
        location=(0.1 * scale * side_mult, 0, 0.38 * scale),
        vertices=16
    )
    lower1 = bpy.context.active_object
    lower1.name = f"Leg_Lower1_{side}"
    parts.append(lower1)

    # Lower leg segment 2 (inner, telescopes out when standing)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.045 * scale,
        depth=0.18 * scale,
        location=(0.1 * scale * side_mult, 0, 0.28 * scale),  # Compressed inside segment 1
        vertices=16
    )
    lower2 = bpy.context.active_object
    lower2.name = f"Leg_Lower2_{side}"
    parts.append(lower2)

    # Ankle ball joint
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.04 * scale,
        location=(0.1 * scale * side_mult, 0, 0.08 * scale),
        segments=16,
        ring_count=12
    )
    ankle = bpy.context.active_object
    ankle.name = f"Leg_Ankle_{side}"
    parts.append(ankle)

    # Foot (elongated, for kneeling pose will be folded back)
    bpy.ops.mesh.primitive_cube_add(
        size=0.14 * scale,
        location=(0.1 * scale * side_mult, 0.09 * scale, 0.02 * scale)
    )
    foot = bpy.context.active_object
    foot.name = f"Leg_Foot_{side}"
    foot.scale = (0.5, 1.5, 0.3)
    bpy.ops.object.transform_apply(scale=True)
    parts.append(foot)

    # Join leg parts
    bpy.ops.object.select_all(action='DESELECT')
    for part in parts:
        part.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()

    leg = bpy.context.active_object
    leg.name = f"Leg_{side}"
    bpy.ops.object.shade_smooth()

    return leg

def create_bronze_robe(scale):
    """Create bronze 'fabric' robe (metallic geometric folds)"""
    print("  Creating bronze robe...")

    # Create circle at waist
    bpy.ops.mesh.primitive_circle_add(
        radius=0.3 * scale,
        vertices=32,
        location=(0, 0, 0.95 * scale)
    )
    robe_base = bpy.context.active_object

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')

    # Extrude down and scale out (cone/bell shape)
    bpy.ops.mesh.extrude_region_move(
        TRANSFORM_OT_translate={"value": (0, 0, -0.4 * scale)}
    )
    bpy.ops.transform.resize(value=(1.4, 1.4, 1.0))

    # Extrude to ground
    bpy.ops.mesh.extrude_region_move(
        TRANSFORM_OT_translate={"value": (0, 0, -0.55 * scale)}
    )
    bpy.ops.transform.resize(value=(1.3, 1.3, 1.0))

    bpy.ops.object.mode_set(mode='OBJECT')

    # Add solidify
    solidify = robe_base.modifiers.new(name="Solidify", type='SOLIDIFY')
    solidify.thickness = 0.005 * scale

    # Add subdivision for smooth but geometric folds
    subdiv = robe_base.modifiers.new(name="Subdiv", type='SUBSURF')
    subdiv.levels = 1
    subdiv.render_levels = 2

    robe_base.name = "Robe_Bronze"
    bpy.ops.object.shade_smooth()

    print(f"    Robe: {len(robe_base.data.vertices)} vertices (bronze cloth)")
    return robe_base

def create_halo_mechanism(scale):
    """Create floating mechanical halo with rotating gears"""
    print("  Creating halo mechanism...")

    halo_z = 1.98 * scale  # Behind head
    halo_y = 0.1 * scale  # 10cm back

    parts = []

    # Outer ring
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.25 * scale,
        minor_radius=0.015 * scale,
        location=(0, halo_y, halo_z),
        major_segments=48,
        minor_segments=12
    )
    outer_ring = bpy.context.active_object
    outer_ring.name = "Halo_Outer_Ring"
    parts.append(outer_ring)

    # Add lotus petal decorations
    for i in range(12):
        angle = (i / 12) * 2 * math.pi
        x = math.cos(angle) * 0.25 * scale
        y = halo_y + math.sin(angle) * 0.25 * scale

        bpy.ops.mesh.primitive_cone_add(
            radius1=0.02 * scale,
            radius2=0,
            depth=0.04 * scale,
            location=(x, y, halo_z),
            vertices=6
        )
        petal = bpy.context.active_object
        petal.rotation_euler = (math.radians(90), 0, angle)
        bpy.ops.object.transform_apply(rotation=True)
        parts.append(petal)

    # Middle gear ring (rotates)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.20 * scale,
        depth=0.02 * scale,
        location=(0, halo_y, halo_z),
        vertices=50
    )
    mid_gear = bpy.context.active_object
    mid_gear.name = "Halo_Gear_Mid"
    parts.append(mid_gear)

    # Inner gear ring (counter-rotates)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.15 * scale,
        depth=0.025 * scale,
        location=(0, halo_y, halo_z + 0.01 * scale),
        vertices=40
    )
    inner_gear = bpy.context.active_object
    inner_gear.name = "Halo_Gear_Inner"
    parts.append(inner_gear)

    # Center hub
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.10 * scale,
        depth=0.03 * scale,
        location=(0, halo_y, halo_z + 0.02 * scale),
        vertices=32
    )
    hub = bpy.context.active_object
    hub.name = "Halo_Hub"
    parts.append(hub)

    # Join all halo parts
    bpy.ops.object.select_all(action='DESELECT')
    for part in parts:
        part.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()

    halo = bpy.context.active_object
    halo.name = "Halo_Complete"
    bpy.ops.object.shade_smooth()

    print(f"    Halo: {len(halo.data.vertices)} vertices (floating mechanism)")
    return halo

# ============================================================================
# MATERIALS - The Penitent Mechanism Aesthetics
# ============================================================================

def create_material_ivory():
    """Pale ivory material (unpainted wood/bone)"""
    mat = bpy.data.materials.new(name="MAT_Ivory")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()

    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.96, 0.94, 0.90, 1.0)  # Pale bone
    bsdf.inputs['Metallic'].default_value = 0.0
    bsdf.inputs['Roughness'].default_value = 0.3
    bsdf.inputs['Subsurface'].default_value = 0.05
    bsdf.inputs['Subsurface Color'].default_value = (0.98, 0.95, 0.88, 1.0)

    output = nodes.new(type='ShaderNodeOutputMaterial')
    mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    return mat

def create_material_bronze():
    """Aged oxidized bronze (dark brown + green verdigris)"""
    mat = bpy.data.materials.new(name="MAT_Bronze")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()

    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    bsdf.inputs['Base Color'].default_value = (0.29, 0.22, 0.13, 1.0)  # Dark bronze
    bsdf.inputs['Metallic'].default_value = 0.9
    bsdf.inputs['Roughness'].default_value = 0.55

    # Add verdigris with noise
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.location = (-400, -200)
    noise.inputs['Scale'].default_value = 8.0

    mix_rgb = nodes.new(type='ShaderNodeMixRGB')
    mix_rgb.location = (-200, 0)
    mix_rgb.inputs['Color1'].default_value = (0.29, 0.22, 0.13, 1.0)  # Bronze
    mix_rgb.inputs['Color2'].default_value = (0.35, 0.47, 0.40, 1.0)  # Green patina

    links = mat.node_tree.links
    links.new(noise.outputs['Fac'], mix_rgb.inputs['Fac'])
    links.new(mix_rgb.outputs['Color'], bsdf.inputs['Base Color'])

    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (200, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    return mat

def create_material_saffron_bronze():
    """Tarnished saffron brass for robe"""
    mat = bpy.data.materials.new(name="MAT_Saffron_Bronze")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()

    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.77, 0.58, 0.24, 1.0)  # Saffron brass
    bsdf.inputs['Metallic'].default_value = 0.85
    bsdf.inputs['Roughness'].default_value = 0.6

    output = nodes.new(type='ShaderNodeOutputMaterial')
    mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    return mat

def create_material_amber_glow():
    """Amber emissive glow for eyes and mechanisms"""
    mat = bpy.data.materials.new(name="MAT_Amber_Glow")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()

    emission = nodes.new(type='ShaderNodeEmission')
    emission.inputs['Color'].default_value = (1.0, 0.63, 0.0, 1.0)  # Warm amber
    emission.inputs['Strength'].default_value = 0.5  # Subtle glow

    output = nodes.new(type='ShaderNodeOutputMaterial')
    mat.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])

    return mat

def assign_materials_to_objects():
    """Assign correct materials to all objects"""
    print("Assigning materials...")

    # Create materials
    mat_ivory = create_material_ivory()
    mat_bronze = create_material_bronze()
    mat_saffron = create_material_saffron_bronze()
    mat_glow = create_material_amber_glow()

    # Assignment logic
    for obj in bpy.data.objects:
        if obj.type != 'MESH' and obj.type != 'CURVE':
            continue

        # Clear existing materials
        obj.data.materials.clear()

        name = obj.name.lower()

        # Ivory objects (left side, body, neck flesh)
        if any(x in name for x in ['body', 'neck_flesh', 'arm_l', 'hand_fused_l', 'leg_l']):
            obj.data.materials.append(mat_ivory)

        # Bronze objects (right side, mask, collars, mechanisms)
        elif any(x in name for x in ['face_mask', 'neck_collar', 'arm_r', 'hand_fused_r',
                                      'leg_r', 'shoulder', 'gear', 'halo', 'mechanism']):
            obj.data.materials.append(mat_bronze)

        # Saffron bronze (robe)
        elif 'robe' in name:
            obj.data.materials.append(mat_saffron)

        # Amber glow (eyes)
        elif 'eye_glow' in name:
            obj.data.materials.append(mat_glow)

        # Hair - gradient from ivory to bronze
        elif 'hair' in name:
            # First 16 strands ivory (hair), rest bronze (cables)
            try:
                idx = int(name.split('_')[-1])
                if idx < 16:
                    obj.data.materials.append(mat_ivory)
                else:
                    obj.data.materials.append(mat_bronze)
            except:
                obj.data.materials.append(mat_ivory)

    print("✓ Materials assigned")

# ============================================================================
# ASSEMBLY & RIGGING (Preserved from original)
# ============================================================================

def setup_armature_and_rig():
    """Generate rig and bind mesh"""
    print("Setting up armature...")

    rig = bpy.data.objects.get('Penitent_Rig')
    if rig:
        print("Using existing rig")
        return rig

    metarig = bpy.data.objects.get('Penitent_MetaRig')
    if not metarig:
        print("Creating new armature...")
        metarig = create_extended_humanoid_armature()

    bpy.context.view_layer.objects.active = metarig
    metarig.select_set(True)

    # Try Rigify generation
    if metarig.name == 'Penitent_MetaRig':
        try:
            bpy.ops.pose.rigify_generate()
            rig = bpy.context.active_object
            rig.name = "Penitent_Rig"
            print("✓ Rigify rig generated")
        except Exception as e:
            print(f"⚠ Rigify failed: {e}, using meta-rig")
            rig = metarig
            rig.name = "Penitent_Rig"
    else:
        rig = metarig

    return rig

def apply_automatic_weights(rig):
    """Apply automatic skinning"""
    print("Applying automatic weights...")

    bpy.ops.object.select_all(action='DESELECT')

    mesh_objects = [obj for obj in bpy.context.scene.objects
                    if obj.type == 'MESH'
                    and not obj.name.startswith('WGT-')
                    and 'Hair' not in obj.name  # Hair uses physics, not skinning
                    and obj.name in bpy.context.view_layer.objects]

    print(f"Found {len(mesh_objects)} mesh objects to rig")

    for mesh_obj in mesh_objects:
        mesh_obj.select_set(True)

    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig

    if len(mesh_objects) > 0:
        try:
            bpy.ops.object.parent_set(type='ARMATURE_AUTO')
            print("✓ Automatic weights applied")
        except Exception as e:
            print(f"⚠ Warning: Automatic weights failed: {e}")
    else:
        print("⚠ Warning: No mesh objects found to rig!")

def log_scene_statistics():
    """Log scene statistics"""
    print("\n" + "=" * 60)
    print("SCENE STATISTICS")
    print("=" * 60)

    mesh_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH']
    if mesh_objects:
        total_verts = sum(len(obj.data.vertices) for obj in mesh_objects)
        total_faces = sum(len(obj.data.polygons) for obj in mesh_objects)
        print(f"Mesh statistics:")
        print(f"  Total vertices: {total_verts}")
        print(f"  Total faces: {total_faces}")
        print(f"  Mesh objects: {len(mesh_objects)}")

    armatures = [obj for obj in bpy.data.objects if obj.type == 'ARMATURE']
    if armatures:
        print(f"\nArmature statistics:")
        for arm in armatures:
            bone_count = len(arm.data.bones)
            print(f"  {arm.name}: {bone_count} bones")

    print(f"\nMaterials: {len(bpy.data.materials)}")
    print("=" * 60 + "\n")

# ============================================================================
# MAIN GENERATION PIPELINE
# ============================================================================

def main():
    """Main generation pipeline for The Penitent Mechanism"""
    import os
    import sys

    print("=" * 60)
    print("THE PENITENT MECHANISM - Procedural Avatar Generation")
    print("=" * 60)
    print(f"Blender version: {bpy.app.version_string}")
    print(f"Python version: {sys.version}")
    print(f"Target height: {AVATAR_HEIGHT}m (standing), ~1.4m (kneeling)")
    print(f"Working directory: {os.getcwd()}")
    print("=" * 60 + "\n")

    try:
        scale = AVATAR_HEIGHT / 1.7

        # Step 1: Clear scene
        print("STEP 1: Clearing scene...")
        clear_scene()

        # Step 2: Create armature
        print("\nSTEP 2: Creating armature...")
        metarig = create_extended_humanoid_armature()

        # Step 3: Create body parts
        print("\nSTEP 3: Creating body mesh...")
        body = create_body_statue(scale)

        print("\nSTEP 4: Creating segmented neck...")
        neck = create_segmented_neck(scale)

        print("\nSTEP 5: Creating bronze mask face...")
        mask = create_bronze_mask_face(scale)

        print("\nSTEP 6: Creating eye glows...")
        eye_left = create_eye_glow(scale, -0.048, 1.885, "L")
        eye_right = create_eye_glow(scale, 0.048, 1.885, "R")

        print("\nSTEP 7: Creating hair with cables...")
        hair_strands = create_ivory_hair_with_cables(scale)

        print("\nSTEP 8: Creating fused hands...")
        hand_left = create_fused_hand(scale, 'L')
        hand_right = create_fused_hand(scale, 'R')

        print("\nSTEP 9: Creating arms...")
        arm_left = create_arm_segment(scale, 'L', is_bronze=False)  # Ivory
        arm_right = create_arm_segment(scale, 'R', is_bronze=True)  # Bronze

        print("\nSTEP 10: Creating shoulder mechanism...")
        shoulder_mech = create_shoulder_mechanism(scale)

        print("\nSTEP 11: Creating telescoping legs...")
        leg_left = create_telescoping_legs(scale, 'L')
        leg_right = create_telescoping_legs(scale, 'R')

        print("\nSTEP 12: Creating bronze robe...")
        robe = create_bronze_robe(scale)

        print("\nSTEP 13: Creating halo mechanism...")
        halo = create_halo_mechanism(scale)

        print("\nSTEP 14: Assigning materials...")
        assign_materials_to_objects()

        print("\nSTEP 15: Setting up rigging...")
        rig = setup_armature_and_rig()

        print("\nSTEP 16: Applying skinning...")
        apply_automatic_weights(rig)

        # Log statistics
        log_scene_statistics()

        print("=" * 60)
        print("✓ AVATAR GENERATION COMPLETE!")
        print("=" * 60)

        # Save file
        output_path = os.path.abspath("Avatar/ForgottenArchitect.blend")
        print(f"\nSaving to: {output_path}")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=output_path)
        print(f"✓ File saved successfully!")

        file_size = os.path.getsize(output_path)
        print(f"✓ File size: {file_size / 1024:.1f} KB")

        if file_size < 10000:
            print("⚠ WARNING: File size very small - generation may have failed!")
            return

        print("\n" + "=" * 60)
        print("✓ The Penitent Mechanism created successfully!")
        print("=" * 60)

    except Exception as e:
        print("\n" + "=" * 60)
        print("✗ FATAL ERROR DURING GENERATION")
        print("=" * 60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 60)
        raise

if __name__ == "__main__":
    main()
