#!/usr/bin/env python3
"""
The Penitent Mechanism - Avatar Generator V4.0
Professional character pipeline with kitbashed mechanical assets

ARCHITECTURE V4.0:
- V1/V2: Built from UV spheres and cylinders (snowman result)
- V3: Attempted base mesh + kitbashing but still used primitives
- V4: TRUE kitbashing - base mesh (Skin Modifier) + pre-modeled mechanical assets

This produces professional character topology suitable for VRChat.
"""

import bpy
import bmesh
import math
import os
import random
from mathutils import Vector, Euler

# Paths
BASEMESH_PATH = os.path.abspath("Avatar/BaseMeshes/PenitentMechanism_Base.blend")
KITBASH_DIR = os.path.abspath("Avatar/Kitbash/")
OUTPUT_PATH = os.path.abspath("Avatar/PenitentMechanism.blend")

# Configuration
KNEELING_HEIGHT = 1.8  # meters
STANDING_HEIGHT = 2.4  # meters

# ============================================================================
# ARMATURE/BONE UTILITIES
# ============================================================================

def find_armature():
    """Find the armature in the scene"""
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE':
            return obj
    return None

def get_bone_world_position(armature, bone_name):
    """Get world position of a bone's head"""
    if armature is None:
        return None

    # Try exact match first
    if bone_name in armature.data.bones:
        bone = armature.data.bones[bone_name]
        return armature.matrix_world @ bone.head_local

    # Try common variations
    variations = [
        bone_name,
        bone_name.replace('.', '_'),
        bone_name.lower(),
        bone_name.upper(),
        f"DEF-{bone_name}",
        f"ORG-{bone_name}",
    ]

    for var in variations:
        if var in armature.data.bones:
            bone = armature.data.bones[var]
            return armature.matrix_world @ bone.head_local

    return None

def get_bone_world_tail(armature, bone_name):
    """Get world position of a bone's tail"""
    if armature is None:
        return None

    if bone_name in armature.data.bones:
        bone = armature.data.bones[bone_name]
        return armature.matrix_world @ bone.tail_local

    return None

def find_bone_by_pattern(armature, patterns):
    """Find a bone matching any of the given patterns"""
    if armature is None:
        return None, None

    for bone in armature.data.bones:
        bone_lower = bone.name.lower()
        for pattern in patterns:
            if pattern.lower() in bone_lower:
                pos = armature.matrix_world @ bone.head_local
                return bone.name, pos

    return None, None

def prepare_mesh_for_merge(obj, armature, bone_name):
    """
    Assigns vertices to a Vertex Group matching the bone name (Rigid Skinning).
    Does NOT parent the object yet. We will merge all objects later.
    """
    if armature is None:
        return False

    # 1. Find actual bone name
    actual_bone_name = None
    for bone in armature.data.bones:
        if bone_name.lower() in bone.name.lower():
            actual_bone_name = bone.name
            break

    if not actual_bone_name:
        print(f"    ⚠ Bone '{bone_name}' not found for binding")
        return False

    # 2. Create Vertex Group and assign all verts with weight 1.0
    # This ensures that when merged, these vertices stick to this bone
    vg = obj.vertex_groups.new(name=actual_bone_name)
    verts = [v.index for v in obj.data.vertices]
    vg.add(verts, 1.0, 'REPLACE')

    print(f"    ✓ Assigned {obj.name} vertices to group '{actual_bone_name}'")
    return True

def merge_all_meshes(base_mesh, armature):
    """Combine all mesh objects into one for VRChat optimization (Draw Calls)"""
    print("  Merging all meshes into single body...")

    # Select base mesh as active
    bpy.ops.object.select_all(action='DESELECT')
    base_mesh.select_set(True)
    bpy.context.view_layer.objects.active = base_mesh

    # Select all other meshes (excluding Rigify widgets)
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH' and obj != base_mesh:
            # Skip Rigify widget objects (they're in a different collection)
            if obj.name.startswith('WGT-'):
                continue
            # Check if object is in current view layer
            if obj.name not in bpy.context.view_layer.objects:
                continue
            obj.select_set(True)
            # Apply all modifiers (Bevels etc) before joining to freeze geometry
            # But do NOT apply Armature modifiers if they exist
            bpy.context.view_layer.objects.active = obj
            for mod in obj.modifiers:
                if mod.type != 'ARMATURE':
                    try:
                        bpy.ops.object.modifier_apply(modifier=mod.name)
                    except:
                        pass  # Skip if modifier can't be applied

    # Join
    bpy.context.view_layer.objects.active = base_mesh
    bpy.ops.object.join()

    # Ensure Armature Modifier exists on final mesh
    if not any(m.type == 'ARMATURE' for m in base_mesh.modifiers):
        mod = base_mesh.modifiers.new(name="Armature", type='ARMATURE')
        mod.object = armature

    # Parent final mesh to armature
    base_mesh.parent = armature
    print(f"    ✓ Merged into '{base_mesh.name}' ({len(base_mesh.data.vertices)} verts)")

def parent_to_bone(obj, armature, bone_name):
    """Parent object to a specific bone"""
    if armature is None:
        print(f"    ⚠ No armature found, cannot parent {obj.name} to bone")
        return False

    # Find bone
    actual_bone_name = None
    for bone in armature.data.bones:
        if bone_name.lower() in bone.name.lower():
            actual_bone_name = bone.name
            break

    if actual_bone_name is None:
        print(f"    ⚠ Bone '{bone_name}' not found, parenting to armature object")
        obj.parent = armature
        return False

    # Parent to bone
    obj.parent = armature
    obj.parent_type = 'BONE'
    obj.parent_bone = actual_bone_name

    print(f"    ✓ Parented {obj.name} to bone '{actual_bone_name}'")
    return True

def get_mesh_bounds(obj):
    """Get world-space bounding box of a mesh"""
    if obj.type != 'MESH':
        return None, None

    # Get world-space bounds
    bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]

    min_z = min(v.z for v in bbox)
    max_z = max(v.z for v in bbox)
    center = sum(bbox, Vector()) / 8

    return center, (min_z, max_z)

def clear_scene():
    """Clear default scene objects"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    # Clear orphan data
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)

    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)

def import_basemesh(filepath, object_name):
    """Import base mesh from .blend file"""
    print(f"Importing base mesh from: {filepath}")

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Base mesh not found: {filepath}")

    # Import all objects from the base mesh file
    with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
        data_to.objects = [name for name in data_from.objects if object_name in name]

    # Link imported objects to scene
    for obj in data_to.objects:
        if obj is not None:
            bpy.context.collection.objects.link(obj)
            print(f"  ✓ Imported: {obj.name} ({len(obj.data.vertices)} verts)")
            return obj

    raise RuntimeError(f"Failed to import {object_name} from {filepath}")

def import_kitbash_asset(asset_filename):
    """
    Import kitbash asset from Avatar/Kitbash directory.
    Returns the imported object.
    """
    filepath = os.path.join(KITBASH_DIR, asset_filename)
    print(f"  Importing kitbash asset: {asset_filename}")

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Kitbash asset not found: {filepath}")

    # Import all objects from the file
    with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
        data_to.objects = data_from.objects

    # Link imported objects to scene and return the main one
    imported_objects = []
    for obj in data_to.objects:
        if obj is not None:
            bpy.context.collection.objects.link(obj)
            imported_objects.append(obj)

    if not imported_objects:
        raise RuntimeError(f"No objects found in {asset_filename}")

    # Return the largest object (usually the main assembly)
    main_obj = max(imported_objects, key=lambda o: len(o.data.vertices) if o.type == 'MESH' else 0)
    print(f"    ✓ Loaded: {main_obj.name} ({len(main_obj.data.vertices)} verts)")
    return main_obj, imported_objects

# ============================================================================
# MULTI-LAYER PROCEDURAL MATERIALS
# ============================================================================

def create_material_bronze_v3():
    """
    Advanced bronze material with 3-layer procedural textures:
    - Layer 1: Base bronze color variation
    - Layer 2: Verdigris/patina (green oxidation)
    - Layer 3: Dirt and weathering
    """
    mat = bpy.data.materials.new(name="MAT_Bronze_V3")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    # Output
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)

    # Principled BSDF
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    bsdf.inputs['Metallic'].default_value = 0.95
    bsdf.inputs['Roughness'].default_value = 0.55

    # Layer 1: Base bronze color variation
    noise_base = nodes.new('ShaderNodeTexNoise')
    noise_base.location = (-600, 200)
    noise_base.inputs['Scale'].default_value = 12.0
    noise_base.inputs['Detail'].default_value = 3.0

    ramp_base = nodes.new('ShaderNodeValToRGB')
    ramp_base.location = (-300, 200)
    ramp_base.color_ramp.elements[0].color = (0.12, 0.08, 0.05, 1.0)  # Dark bronze
    ramp_base.color_ramp.elements[1].color = (0.22, 0.16, 0.09, 1.0)  # Light bronze

    # Layer 2: Verdigris (green oxidation)
    noise_verdigris = nodes.new('ShaderNodeTexNoise')
    noise_verdigris.location = (-600, -100)
    noise_verdigris.inputs['Scale'].default_value = 6.0
    noise_verdigris.inputs['Detail'].default_value = 2.0
    noise_verdigris.inputs['Roughness'].default_value = 0.65

    ramp_verdigris = nodes.new('ShaderNodeValToRGB')
    ramp_verdigris.location = (-300, -100)
    ramp_verdigris.color_ramp.elements[0].position = 0.45
    ramp_verdigris.color_ramp.elements[0].color = (0, 0, 0, 1)  # No verdigris
    ramp_verdigris.color_ramp.elements[1].color = (0.1, 0.3, 0.2, 1)  # Green patina

    # Layer 3: Dirt/weathering
    noise_dirt = nodes.new('ShaderNodeTexNoise')
    noise_dirt.location = (-600, -400)
    noise_dirt.inputs['Scale'].default_value = 20.0
    noise_dirt.inputs['Detail'].default_value = 5.0

    ramp_dirt = nodes.new('ShaderNodeValToRGB')
    ramp_dirt.location = (-300, -400)
    ramp_dirt.color_ramp.elements[0].position = 0.6
    ramp_dirt.color_ramp.elements[0].color = (0, 0, 0, 1)  # Clean
    ramp_dirt.color_ramp.elements[1].color = (0.05, 0.04, 0.03, 1)  # Dirt

    # Mix layers
    mix_verdigris = nodes.new('ShaderNodeMixRGB')
    mix_verdigris.location = (0, 0)
    mix_verdigris.blend_type = 'MIX'
    mix_verdigris.inputs['Fac'].default_value = 0.3

    mix_dirt = nodes.new('ShaderNodeMixRGB')
    mix_dirt.location = (150, 0)
    mix_dirt.blend_type = 'MULTIPLY'
    mix_dirt.inputs['Fac'].default_value = 0.4

    # Roughness variation
    noise_roughness = nodes.new('ShaderNodeTexNoise')
    noise_roughness.location = (-300, -600)
    noise_roughness.inputs['Scale'].default_value = 15.0

    map_range_rough = nodes.new('ShaderNodeMapRange')
    map_range_rough.location = (0, -600)
    map_range_rough.inputs['From Min'].default_value = 0.0
    map_range_rough.inputs['From Max'].default_value = 1.0
    map_range_rough.inputs['To Min'].default_value = 0.45
    map_range_rough.inputs['To Max'].default_value = 0.75

    # Connect nodes
    links.new(noise_base.outputs['Fac'], ramp_base.inputs['Fac'])
    links.new(noise_verdigris.outputs['Fac'], ramp_verdigris.inputs['Fac'])
    links.new(noise_dirt.outputs['Fac'], ramp_dirt.inputs['Fac'])

    links.new(ramp_base.outputs['Color'], mix_verdigris.inputs['Color1'])
    links.new(ramp_verdigris.outputs['Color'], mix_verdigris.inputs['Color2'])
    links.new(mix_verdigris.outputs['Color'], mix_dirt.inputs['Color1'])
    links.new(ramp_dirt.outputs['Color'], mix_dirt.inputs['Color2'])

    links.new(mix_dirt.outputs['Color'], bsdf.inputs['Base Color'])

    links.new(noise_roughness.outputs['Fac'], map_range_rough.inputs['Value'])
    links.new(map_range_rough.outputs['Result'], bsdf.inputs['Roughness'])

    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    return mat

def create_material_ivory_v3():
    """
    Upgraded ivory with subtle variation instead of flat color
    """
    mat = bpy.data.materials.new(name="MAT_Ivory_V3")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (400, 0)

    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (200, 0)
    bsdf.inputs['Metallic'].default_value = 0.0
    bsdf.inputs['Specular'].default_value = 0.3

    # Subtle color variation
    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-400, 0)
    noise.inputs['Scale'].default_value = 18.0
    noise.inputs['Detail'].default_value = 2.0

    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (-200, 0)
    ramp.color_ramp.elements[0].color = (0.85, 0.82, 0.75, 1.0)  # Ivory
    ramp.color_ramp.elements[1].color = (0.92, 0.90, 0.85, 1.0)  # Lighter ivory

    # Roughness variation
    noise_rough = nodes.new('ShaderNodeTexNoise')
    noise_rough.location = (-400, -200)
    noise_rough.inputs['Scale'].default_value = 25.0

    map_range = nodes.new('ShaderNodeMapRange')
    map_range.location = (-200, -200)
    map_range.inputs['To Min'].default_value = 0.35
    map_range.inputs['To Max'].default_value = 0.55

    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    links.new(noise_rough.outputs['Fac'], map_range.inputs['Value'])
    links.new(map_range.outputs['Result'], bsdf.inputs['Roughness'])

    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    return mat

def create_material_saffron_bronze_v3():
    """Warm brass with subtle procedural detail"""
    mat = bpy.data.materials.new(name="MAT_Saffron_Bronze_V3")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (400, 0)

    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (200, 0)
    bsdf.inputs['Metallic'].default_value = 0.85

    # Color variation
    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-400, 0)
    noise.inputs['Scale'].default_value = 15.0

    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (-200, 0)
    ramp.color_ramp.elements[0].color = (0.65, 0.45, 0.15, 1.0)  # Dark brass
    ramp.color_ramp.elements[1].color = (0.80, 0.60, 0.25, 1.0)  # Light brass

    noise_rough = nodes.new('ShaderNodeTexNoise')
    noise_rough.location = (-400, -200)
    noise_rough.inputs['Scale'].default_value = 20.0

    map_range = nodes.new('ShaderNodeMapRange')
    map_range.location = (-200, -200)
    map_range.inputs['To Min'].default_value = 0.40
    map_range.inputs['To Max'].default_value = 0.65

    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(noise_rough.outputs['Fac'], map_range.inputs['Value'])
    links.new(map_range.outputs['Result'], bsdf.inputs['Roughness'])
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    return mat

def create_material_amber_glow_v3():
    """Enhanced emission material"""
    mat = bpy.data.materials.new(name="MAT_Amber_Glow_V3")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (200, 0)

    emission = nodes.new('ShaderNodeEmission')
    emission.location = (0, 0)
    emission.inputs['Color'].default_value = (1.0, 0.6, 0.2, 1.0)  # Amber
    emission.inputs['Strength'].default_value = 3.0

    links.new(emission.outputs['Emission'], output.inputs['Surface'])

    return mat

# ============================================================================
# GEOMETRIC DETAIL HELPERS
# ============================================================================

def add_panel_lines(obj, num_lines=5):
    """Add panel lines to object using edge bevels"""
    print(f"  Adding panel lines to {obj.name}...")

    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')

    bm = bmesh.from_edit_mesh(obj.data)

    # Select random horizontal edges
    random.seed(42)
    edges_to_bevel = []
    for edge in bm.edges:
        if random.random() < (num_lines / len(bm.edges)):
            edges_to_bevel.append(edge)

    # Bevel selected edges
    if edges_to_bevel:
        for edge in edges_to_bevel:
            edge.select = True

        bmesh.ops.bevel(bm, geom=edges_to_bevel, offset=0.002, segments=2)
        bmesh.update_edit_mesh(obj.data)

    bpy.ops.object.mode_set(mode='OBJECT')

def add_bolts_to_object(obj, count=8):
    """Add bolt details at strategic points"""
    print(f"  Adding {count} bolts to {obj.name}...")

    random.seed(123)
    vertices = obj.data.vertices

    for i in range(count):
        # Pick random vertex
        vert_idx = random.randint(0, len(vertices) - 1)
        vert_co = obj.matrix_world @ vertices[vert_idx].co

        # Create bolt (small cylinder)
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=6,
            radius=0.008,
            depth=0.015,
            location=vert_co
        )
        bolt = bpy.context.active_object
        bolt.name = f"Bolt_{obj.name}_{i}"
        bolt.parent = obj

def add_surface_weathering(obj):
    """Add weathering details via displacement"""
    print(f"  Adding weathering to {obj.name}...")

    # Add displacement modifier with noise texture
    displace = obj.modifiers.new(name="Weathering", type='DISPLACE')
    displace.strength = 0.005
    displace.mid_level = 0.5

    # Create noise texture
    tex = bpy.data.textures.new(name=f"Weathering_{obj.name}", type='CLOUDS')
    tex.noise_scale = 0.5
    tex.noise_depth = 3

    displace.texture = tex

# ============================================================================
# BODY MODIFICATION (transform human mesh into mechanical statue)
# ============================================================================

def add_bronze_mask(base_mesh, armature):
    """Add a bronze mask covering the face - no nose, no mouth, only eye slits"""
    print("Adding bronze mask to cover face...")

    # Find head bone position
    head_bone, head_pos = find_bone_by_pattern(armature, ['head', 'skull'])

    if head_pos:
        mask_pos = head_pos + Vector((0, 0.02, 0.05))
    else:
        # Fallback
        center, (min_z, max_z) = get_mesh_bounds(base_mesh)
        if center:
            mask_pos = Vector((center.x, center.y + 0.02, max_z - 0.15))
        else:
            mask_pos = Vector((0, 0.02, 1.65))

    # Create mask base (elongated sphere, flattened)
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=16,
        ring_count=12,
        radius=0.12,
        location=mask_pos
    )
    mask = bpy.context.active_object
    mask.name = "Bronze_Mask"

    # Flatten and shape the mask
    mask.scale = (0.9, 0.6, 1.1)  # Taller, flatter
    bpy.ops.object.transform_apply(scale=True)

    # Add eye slits (boolean cutouts)
    for side in [-1, 1]:
        bpy.ops.mesh.primitive_cube_add(
            size=0.03,
            location=(mask_pos.x + side * 0.035, mask_pos.y - 0.08, mask_pos.z + 0.02)
        )
        eye_cutter = bpy.context.active_object
        eye_cutter.scale = (1.5, 2.0, 0.3)  # Almond shape
        eye_cutter.rotation_euler = (0, 0, math.radians(side * 10))

        # Apply boolean
        bool_mod = mask.modifiers.new(name=f"Eye_{side}", type='BOOLEAN')
        bool_mod.operation = 'DIFFERENCE'
        bool_mod.object = eye_cutter

        # Apply modifier
        bpy.context.view_layer.objects.active = mask
        bpy.ops.object.modifier_apply(modifier=bool_mod.name)

        # Delete cutter
        bpy.data.objects.remove(eye_cutter, do_unlink=True)

    # Add forehead ridge
    bpy.ops.mesh.primitive_cube_add(
        size=0.15,
        location=(mask_pos.x, mask_pos.y - 0.03, mask_pos.z + 0.08)
    )
    ridge = bpy.context.active_object
    ridge.scale = (1.2, 0.2, 0.15)
    bpy.ops.object.transform_apply(scale=True)

    # Join ridge to mask
    bpy.ops.object.select_all(action='DESELECT')
    ridge.select_set(True)
    mask.select_set(True)
    bpy.context.view_layer.objects.active = mask
    bpy.ops.object.join()

    # Parent to head bone
    # Prepare for merge instead of parenting
    if armature and head_bone:
        prepare_mesh_for_merge(mask, armature, head_bone)

    print(f"    ✓ Bronze mask created ({len(mask.data.vertices)} verts)")
    return mask

def delete_hand_geometry(base_mesh):
    """Delete hand vertices from the base mesh (will be replaced by blade hands)"""
    print("Removing hand geometry from base mesh...")

    bpy.context.view_layer.objects.active = base_mesh
    bpy.ops.object.mode_set(mode='EDIT')

    bm = bmesh.from_edit_mesh(base_mesh.data)
    bm.verts.ensure_lookup_table()

    # Find vertices below wrist height and at hand X positions
    # This is approximate - we select vertices at the extremities
    verts_to_delete = []

    # Get mesh bounds
    min_x = min(v.co.x for v in bm.verts)
    max_x = max(v.co.x for v in bm.verts)
    min_z = min(v.co.z for v in bm.verts)
    max_z = max(v.co.z for v in bm.verts)

    # Hand region is roughly:
    # - X: outer 15% on each side
    # - Z: lower 50% of the model (below chest)
    hand_x_threshold = (max_x - min_x) * 0.35
    wrist_z = min_z + (max_z - min_z) * 0.45

    for v in bm.verts:
        # Check if vertex is in hand region
        is_hand_x = abs(v.co.x) > hand_x_threshold
        is_below_wrist = v.co.z < wrist_z

        if is_hand_x and is_below_wrist:
            verts_to_delete.append(v)

    # Delete the vertices
    if verts_to_delete:
        bmesh.ops.delete(bm, geom=verts_to_delete, context='VERTS')
        bmesh.update_edit_mesh(base_mesh.data)
        print(f"    ✓ Deleted {len(verts_to_delete)} hand vertices")
    else:
        print("    ⚠ No hand vertices found to delete")

    bpy.ops.object.mode_set(mode='OBJECT')

def add_body_segmentation(base_mesh):
    """Add segmentation cuts to make body look mechanical/armored"""
    print("Adding body segmentation for mechanical appearance...")

    bpy.context.view_layer.objects.active = base_mesh
    bpy.ops.object.mode_set(mode='EDIT')

    bm = bmesh.from_edit_mesh(base_mesh.data)
    bm.edges.ensure_lookup_table()

    # Get Z range
    min_z = min(v.co.z for v in bm.verts)
    max_z = max(v.co.z for v in bm.verts)
    height = max_z - min_z

    # Select horizontal edge loops at key body segment points
    # Neck, chest, waist, hips, knees
    segment_heights = [0.85, 0.70, 0.55, 0.45, 0.30]

    edges_to_bevel = []
    for ratio in segment_heights:
        target_z = min_z + height * ratio
        tolerance = height * 0.02

        for edge in bm.edges:
            # Check if edge is roughly horizontal at this height
            v1_z = edge.verts[0].co.z
            v2_z = edge.verts[1].co.z

            if abs(v1_z - v2_z) < tolerance:  # Horizontal-ish
                avg_z = (v1_z + v2_z) / 2
                if abs(avg_z - target_z) < tolerance:
                    edges_to_bevel.append(edge)

    # Bevel selected edges for panel line effect
    if edges_to_bevel:
        result = bmesh.ops.bevel(
            bm,
            geom=edges_to_bevel,
            offset=0.003,
            segments=2,
            affect='EDGES'
        )
        print(f"    ✓ Added {len(edges_to_bevel)} segmentation lines")

    bmesh.update_edit_mesh(base_mesh.data)
    bpy.ops.object.mode_set(mode='OBJECT')

def add_body_armor(base_mesh, armature):
    """Import high-fidelity armor set and attach to rig"""
    print("Importing High-Fidelity Armor Set...")

    try:
        # Import the new Armor Set generated by kitbash script
        # This returns the main object, but we need specific parts
        # So we use the list of all imported objects
        _, all_parts = import_kitbash_asset("Armor_Set_01.blend")

        armor_parts = [obj for obj in all_parts if obj.type == 'MESH']

        # Process each armor piece
        for part in armor_parts:
            # 1. CHEST
            if "Chest" in part.name:
                spine_bone, spine_pos = find_bone_by_pattern(armature, ['spine', 'chest'])
                if spine_pos:
                    part.location = spine_pos + Vector((0, -0.02, 0))
                    part.rotation_euler = (0, 0, 0)
                    prepare_mesh_for_merge(part, armature, spine_bone)

            # 2. THIGH/LEGS
            elif "Thigh" in part.name or "Leg" in part.name:
                side = 'L' if 'L' in part.name else 'R'
                bone_name, bone_pos = find_bone_by_pattern(armature, [f'thigh.{side}', f'leg.{side}'])
                if bone_pos:
                    part.location = bone_pos + Vector((0, -0.05, 0))
                    # Mirror X for Right side if needed
                    if side == 'R':
                        part.scale.x *= -1
                        bpy.ops.object.transform_apply(scale=True)
                    prepare_mesh_for_merge(part, armature, bone_name)

            # 3. FOREARMS
            elif "Forearm" in part.name or "Arm" in part.name:
                side = 'L' if 'L' in part.name else 'R'
                bone_name, bone_pos = find_bone_by_pattern(armature, [f'forearm.{side}', f'lower_arm.{side}'])
                if bone_pos:
                    part.location = bone_pos
                    part.rotation_euler = (math.radians(90), 0, 0)
                    if side == 'R':
                        part.scale.x *= -1
                        bpy.ops.object.transform_apply(scale=True)
                    prepare_mesh_for_merge(part, armature, bone_name)

            # 4. PAULDRONS
            elif "Pauldron" in part.name:
                side = 'L' if 'L' in part.name else 'R'
                bone_name, bone_pos = find_bone_by_pattern(armature, [f'shoulder.{side}', f'upper_arm.{side}'])
                if bone_pos:
                    part.location = bone_pos + Vector((0, 0, 0.05))
                    if side == 'R':
                        part.location.x *= -1
                    prepare_mesh_for_merge(part, armature, bone_name)

        print(f"    ✓ Imported and rigged {len(armor_parts)} high-poly armor pieces")
        return armor_parts

    except FileNotFoundError:
        print("    ⚠ Armor Set not found! Run generate_kitbash_assets.py first.")
        return []

def add_neck_segments(base_mesh, armature):
    """Add segmented neck rings for unnatural head rotation"""
    print("Adding segmented neck rings...")

    # Find neck position
    neck_bone, neck_pos = find_bone_by_pattern(armature, ['neck', 'spine'])

    if neck_pos:
        base_pos = neck_pos
    else:
        center, (min_z, max_z) = get_mesh_bounds(base_mesh)
        if center:
            base_pos = Vector((center.x, center.y, max_z * 0.85))
        else:
            base_pos = Vector((0, 0, 1.45))

    neck_rings = []

    # Create 3 stacked rings
    for i in range(3):
        ring_z = base_pos.z + i * 0.025

        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.08 - i * 0.005,
            minor_radius=0.015,
            major_segments=16,
            minor_segments=8,
            location=(base_pos.x, base_pos.y, ring_z)
        )
        ring = bpy.context.active_object
        ring.name = f"Neck_Ring_{i}"
        neck_rings.append(ring)

    # Join all rings
    if len(neck_rings) > 1:
        bpy.ops.object.select_all(action='DESELECT')
        for ring in neck_rings:
            ring.select_set(True)
        bpy.context.view_layer.objects.active = neck_rings[0]
        bpy.ops.object.join()

    neck_assembly = neck_rings[0]
    neck_assembly.name = "Neck_Segments"

    # Parent to neck bone
    if armature:
        neck_bone_name, _ = find_bone_by_pattern(armature, ['neck'])
        if neck_bone_name:
            prepare_mesh_for_merge(neck_assembly, armature, neck_bone_name)

    print(f"    ✓ Neck segments created ({len(neck_assembly.data.vertices)} verts)")
    return neck_assembly

# ============================================================================
# MECHANICAL KITBASH (import pre-modeled assets)
# ============================================================================

def add_shoulder_mechanism(base_mesh, armature):
    """Import and attach pre-modeled shoulder mechanism to shoulder bone"""
    print("Adding shoulder mechanism (kitbash import)...")

    try:
        shoulder, all_parts = import_kitbash_asset("Mech_Shoulder_01.blend")

        # Join all parts into single object
        if len(all_parts) > 1:
            bpy.ops.object.select_all(action='DESELECT')
            for obj in all_parts:
                if obj.type == 'MESH':
                    obj.select_set(True)
            bpy.context.view_layer.objects.active = shoulder
            bpy.ops.object.join()

        # Scale down the shoulder mechanism
        shoulder.scale = (0.5, 0.5, 0.5)
        bpy.ops.object.select_all(action='DESELECT')
        shoulder.select_set(True)
        bpy.context.view_layer.objects.active = shoulder
        bpy.ops.object.transform_apply(scale=True)

        # Find shoulder bone position
        shoulder_bone, shoulder_pos = find_bone_by_pattern(armature, ['shoulder', 'clavicle', 'upper_arm'])

        if shoulder_pos:
            # Position on top of shoulder, not floating
            shoulder.location = shoulder_pos + Vector((0.05, 0, 0.02))
            print(f"    Positioned at bone '{shoulder_bone}': {shoulder.location}")
        else:
            # Fallback: use mesh bounds
            center, (min_z, max_z) = get_mesh_bounds(base_mesh)
            if center:
                shoulder.location = (center.x + 0.15, center.y, max_z * 0.80)
            else:
                shoulder.location = (0.15, 0, 1.35)
            print(f"    Using fallback position: {shoulder.location}")

        shoulder.rotation_euler = (0, 0, math.radians(-15))

        # Parent to shoulder bone
        if armature and shoulder_bone:
            prepare_mesh_for_merge(shoulder, armature, shoulder_bone)

        print(f"    ✓ Shoulder mechanism attached ({len(shoulder.data.vertices)} verts)")
        return [shoulder]

    except FileNotFoundError:
        print("  ⚠ Shoulder asset not found, skipping...")
        return []

def add_mechanical_halo(base_mesh, armature):
    """Import and attach pre-modeled mechanical halo to head bone"""
    print("Creating mechanical halo (kitbash import)...")

    try:
        halo, all_parts = import_kitbash_asset("Mech_Halo_01.blend")

        # Join all parts into single object
        if len(all_parts) > 1:
            bpy.ops.object.select_all(action='DESELECT')
            for obj in all_parts:
                if obj.type == 'MESH':
                    obj.select_set(True)
            bpy.context.view_layer.objects.active = halo
            bpy.ops.object.join()

        # Scale down the halo significantly
        halo.scale = (0.4, 0.4, 0.4)
        bpy.ops.object.select_all(action='DESELECT')
        halo.select_set(True)
        bpy.context.view_layer.objects.active = halo
        bpy.ops.object.transform_apply(scale=True)

        # Find head bone position
        head_bone, head_pos = find_bone_by_pattern(armature, ['head', 'skull'])

        if head_pos:
            # Position just behind and above head (like a saint's halo)
            halo.location = head_pos + Vector((0, 0.08, 0.12))
            print(f"    Positioned above bone '{head_bone}': {halo.location}")
        else:
            # Fallback: use mesh bounds
            center, (min_z, max_z) = get_mesh_bounds(base_mesh)
            if center:
                halo.location = (center.x, center.y + 0.08, max_z + 0.05)
            else:
                halo.location = (0, 0.08, 1.75)
            print(f"    Using fallback position: {halo.location}")

        halo.rotation_euler = (math.radians(15), 0, 0)

        # Parent to head bone
        if armature and head_bone:
            prepare_mesh_for_merge(halo, armature, head_bone)

        print(f"    ✓ Halo attached ({len(halo.data.vertices)} verts)")
        return [halo]

    except FileNotFoundError:
        print("  ⚠ Halo asset not found, skipping...")
        return []

def add_blade_hands(base_mesh, armature):
    """Import and attach pre-modeled blade hands to hand bones"""
    print("Creating blade-hands (kitbash import)...")

    blade_hands = []

    for side in ['L', 'R']:
        sign = 1 if side == 'L' else -1

        try:
            blade, all_parts = import_kitbash_asset(f"BladeHand_{side}.blend")

            # Join all parts if multiple
            if len(all_parts) > 1:
                bpy.ops.object.select_all(action='DESELECT')
                for obj in all_parts:
                    if obj.type == 'MESH':
                        obj.select_set(True)
                bpy.context.view_layer.objects.active = blade
                bpy.ops.object.join()

            # Find hand bone position
            hand_patterns = [f'hand.{side}', f'hand_{side}', f'wrist.{side}', f'wrist_{side}']
            hand_bone, hand_pos = find_bone_by_pattern(armature, hand_patterns)

            if hand_pos:
                # Position at hand bone
                blade.location = hand_pos + Vector((0, 0.05, 0))
                print(f"    Positioned at bone '{hand_bone}': {blade.location}")
            else:
                # Fallback: estimate from mesh bounds
                center, (min_z, max_z) = get_mesh_bounds(base_mesh)
                if center:
                    blade.location = (sign * 0.35, center.y + 0.3, max_z * 0.45)
                else:
                    blade.location = (sign * 0.18, 0.45, 0.70)
                print(f"    Using fallback position: {blade.location}")

            blade.rotation_euler = (math.radians(-20), 0, math.radians(sign * 5))

            # Parent to hand bone
            if armature and hand_bone:
                prepare_mesh_for_merge(blade, armature, hand_bone)

            blade_hands.append(blade)
            print(f"    ✓ Blade hand {side} attached ({len(blade.data.vertices)} verts)")

        except FileNotFoundError:
            print(f"  ⚠ Blade hand {side} asset not found, skipping...")

    return blade_hands

def add_cable_clusters(base_mesh, armature):
    """Import and attach cable clusters to spine/chest bone"""
    print("Adding cable clusters (kitbash import)...")

    try:
        cables, all_parts = import_kitbash_asset("CableCluster_01.blend")

        # Join all cable strands
        if len(all_parts) > 1:
            bpy.ops.object.select_all(action='DESELECT')
            for obj in all_parts:
                if obj.type == 'MESH':
                    obj.select_set(True)
            bpy.context.view_layer.objects.active = cables
            bpy.ops.object.join()

        # Find spine/chest bone position
        spine_bone, spine_pos = find_bone_by_pattern(armature, ['spine', 'chest', 'torso'])

        if spine_pos:
            # Position at spine
            cables.location = spine_pos + Vector((0.15, -0.08, 0.10))
            print(f"    Positioned at bone '{spine_bone}': {cables.location}")
        else:
            # Fallback
            center, (min_z, max_z) = get_mesh_bounds(base_mesh)
            if center:
                cables.location = (center.x + 0.15, center.y - 0.08, max_z * 0.65)
            else:
                cables.location = (0.15, -0.08, 1.05)
            print(f"    Using fallback position: {cables.location}")

        # Parent to spine bone
        if armature and spine_bone:
            prepare_mesh_for_merge(cables, armature, spine_bone)

        print(f"    ✓ Cable cluster attached ({len(cables.data.vertices)} verts)")
        return [cables]

    except FileNotFoundError:
        print("  ⚠ Cable cluster asset not found, skipping...")
        return []

# ============================================================================
# RIGGING
# ============================================================================

def create_rigify_metarig():
    """Create Rigify metarig for humanoid"""
    print("Creating Rigify metarig...")

    # Enable Rigify addon
    bpy.ops.preferences.addon_enable(module='rigify')

    # Add metarig
    bpy.ops.object.armature_human_metarig_add()
    metarig = bpy.context.active_object
    metarig.name = "Penitent_MetaRig"
    metarig.location = (0, 0, 0)

    # Scale to match character
    metarig.scale = (0.85, 0.85, 0.90)
    bpy.ops.object.transform_apply(scale=True)

    return metarig

def generate_rigify_rig(metarig):
    """Generate final rig from metarig"""
    print("Generating Rigify rig...")

    bpy.context.view_layer.objects.active = metarig
    bpy.ops.pose.rigify_generate()

    # Find generated rig
    for obj in bpy.data.objects:
        if "rig" in obj.name.lower() and obj.type == 'ARMATURE' and obj != metarig:
            print(f"  ✓ Generated rig: {obj.name}")
            return obj

    return None

def apply_automatic_weights(mesh_objects, armature):
    """Apply automatic skinning weights"""
    print("Applying automatic weights...")

    for obj in mesh_objects:
        if obj.type != 'MESH':
            continue

        # Skip objects that already have vertex groups (Rigid Skinned objects)
        if len(obj.vertex_groups) > 0:
            continue

        # Select mesh and armature
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        armature.select_set(True)
        bpy.context.view_layer.objects.active = armature

        # Parent with automatic weights
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')
        print(f"  ✓ Weighted: {obj.name}")

# ============================================================================
# MAIN PIPELINE
# ============================================================================

def main():
    """Main avatar generation pipeline - V3 Architecture"""
    import sys

    print("=" * 60)
    print("THE PENITENT MECHANISM - Avatar Generator V4.0")
    print("Architecture: Skin Modifier base + kitbashed mechanical assets")
    print("=" * 60)
    print(f"Blender: {bpy.app.version_string}")
    print(f"Python: {sys.version}")
    print("=" * 60)
    print()

    try:
        # STEP 1: Clear and import base mesh
        print("STEP 1: Importing base mesh...")
        clear_scene()
        basemesh = import_basemesh(BASEMESH_PATH, "PenitentMechanism_Base")

        # Find armature (imported with base mesh)
        armature = find_armature()
        if armature:
            print(f"  ✓ Found armature: {armature.name} ({len(armature.data.bones)} bones)")
            # List some key bones for debugging
            bone_names = [b.name for b in armature.data.bones]
            print(f"  Sample bones: {bone_names[:5]}...")
        else:
            print("  ⚠ No armature found - using fallback positioning")
        print()

        # STEP 2: Create upgraded materials
        print("STEP 2: Creating multi-layer procedural materials...")
        mat_bronze = create_material_bronze_v3()
        mat_ivory = create_material_ivory_v3()
        mat_saffron = create_material_saffron_bronze_v3()
        mat_amber = create_material_amber_glow_v3()
        print("  ✓ 4 materials created with procedural detail")
        print()

        # STEP 3: Body modification - transform into mechanical statue
        print("STEP 3: Transforming body into mechanical statue...")

        # 3a: Delete hand geometry (will be replaced by blade hands)
        delete_hand_geometry(basemesh)

        # 3b: Add body segmentation for mechanical appearance
        add_body_segmentation(basemesh)

        # 3c: Add bronze mask over face
        mask = add_bronze_mask(basemesh, armature)
        if mask:
            mask.data.materials.append(mat_bronze)

        # 3d: Add segmented neck rings
        neck = add_neck_segments(basemesh, armature)
        if neck:
            neck.data.materials.append(mat_bronze)

        # 3e: Add body armor to cover the body
        armor_parts = add_body_armor(basemesh, armature)
        for part in armor_parts:
            if not part.data.materials:
                part.data.materials.append(mat_bronze)

        print("  ✓ Body transformation complete")
        print()

        # STEP 4: Assign bronze material to body (statue, not flesh)
        print("STEP 4: Assigning materials to base mesh...")
        if not basemesh.data.materials:
            basemesh.data.materials.append(mat_bronze)
        else:
            basemesh.data.materials[0] = mat_bronze
        print("  ✓ Base mesh materialed with bronze")
        print()

        # STEP 5: Adding geometric detail
        print("STEP 5: Adding geometric detail...")
        add_panel_lines(basemesh, num_lines=8)
        add_bolts_to_object(basemesh, count=12)
        add_surface_weathering(basemesh)
        print()

        # STEP 6: Add mechanical kitbash
        print("STEP 6: Adding mechanical corruption...")
        shoulder_parts = add_shoulder_mechanism(basemesh, armature)
        for part in shoulder_parts:
            if not part.data.materials:
                part.data.materials.append(mat_bronze)
        print()

        # STEP 7: Add halo
        print("STEP 7: Creating mechanical halo...")
        halo_parts = add_mechanical_halo(basemesh, armature)
        for part in halo_parts:
            if not part.data.materials:
                part.data.materials.append(mat_bronze)
        print()

        # STEP 8: Add blade hands
        print("STEP 8: Creating blade-hands...")
        blade_parts = add_blade_hands(basemesh, armature)
        for part in blade_parts:
            if not part.data.materials:
                part.data.materials.append(mat_bronze)
        print()

        # STEP 9: Add cable clusters
        print("STEP 9: Adding cable clusters...")
        cable_parts = add_cable_clusters(basemesh, armature)
        for part in cable_parts:
            if not part.data.materials:
                part.data.materials.append(mat_bronze)
        print()

        # STEP 10: Setup rigging
        print("STEP 10: Setting up rigging...")
        metarig = create_rigify_metarig()
        rig = generate_rigify_rig(metarig)

        if rig:
            # Collect mesh objects (exclude Rigify widget objects)
            mesh_objects = [obj for obj in bpy.data.objects
                          if obj.type == 'MESH' and not obj.name.startswith('WGT-')]
            apply_automatic_weights(mesh_objects, rig)

            # STEP 10b: MERGE MESHES (Optimization)
            print("STEP 10b: Merging meshes for VRChat optimization...")
            merge_all_meshes(basemesh, rig)
        print()

        # STEP 11: Final statistics
        print("=" * 60)
        print("SCENE STATISTICS")
        print("=" * 60)

        # Statistics (exclude Rigify widgets)
        mesh_objects = [obj for obj in bpy.data.objects
                       if obj.type == 'MESH' and not obj.name.startswith('WGT-')]
        total_verts = sum(len(obj.data.vertices) for obj in mesh_objects)
        total_faces = sum(len(obj.data.polygons) for obj in mesh_objects)
        mesh_count = len(mesh_objects)

        print(f"  Total vertices: {total_verts}")
        print(f"  Total faces: {total_faces}")
        print(f"  Mesh objects: {mesh_count}")
        print(f"  Materials: {len(bpy.data.materials)}")
        print("=" * 60)
        print()

        # STEP 12: Save
        print(f"Saving to: {OUTPUT_PATH}")
        bpy.ops.wm.save_as_mainfile(filepath=OUTPUT_PATH)
        print("✓ File saved!")
        print()

        print("=" * 60)
        print("✓ AVATAR GENERATION COMPLETE (V4 ARCHITECTURE)!")
        print("=" * 60)

    except Exception as e:
        print("\n" + "=" * 60)
        print("✗ FATAL ERROR")
        print("=" * 60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()
