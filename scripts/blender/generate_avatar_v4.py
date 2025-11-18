#!/usr/bin/env python3
"""
The Penitent Mechanism - Avatar Generator V4.0
TRUE kitbashing architecture - imports pre-modeled assets

ARCHITECTURE V4:
- Imports high-quality base mesh (not primitive-generated)
- Imports detailed kitbash assets from .blend files
- Combines, materials, and rigs the final character
- NO procedural primitive generation for character anatomy
"""

import bpy
import bmesh
import math
import os
import random
from mathutils import Vector, Euler

# Paths
BASEMESH_PATH = os.path.abspath("Avatar/BaseMeshes/PenitentMechanism_Base.blend")
KITBASH_DIR = os.path.abspath("Avatar/Kitbash")
OUTPUT_PATH = os.path.abspath("Avatar/ForgottenArchitect.blend")

# Configuration
KNEELING_HEIGHT = 1.8  # meters
STANDING_HEIGHT = 2.4  # meters

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

def import_from_blend(filepath, collection_name=None):
    """
    Import all objects from a .blend file.
    If collection_name is specified, only import from that collection.
    Returns list of imported objects.
    """
    print(f"  Importing from: {os.path.basename(filepath)}")

    if not os.path.exists(filepath):
        print(f"  ⚠ WARNING: File not found: {filepath}")
        return []

    imported_objects = []

    with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
        if collection_name:
            # Import specific collection
            data_to.collections = [collection_name] if collection_name in data_from.collections else []
        else:
            # Import all objects
            data_to.objects = data_from.objects[:]

    # Link imported objects to scene
    if hasattr(data_to, 'collections'):
        for coll in data_to.collections:
            if coll is not None:
                bpy.context.scene.collection.children.link(coll)
                for obj in coll.objects:
                    imported_objects.append(obj)
                    print(f"    ✓ {obj.name}")

    if hasattr(data_to, 'objects'):
        for obj in data_to.objects:
            if obj is not None:
                bpy.context.collection.objects.link(obj)
                imported_objects.append(obj)
                print(f"    ✓ {obj.name}")

    return imported_objects

def import_basemesh():
    """Import the base humanoid mesh"""
    print("Importing base humanoid mesh...")

    if not os.path.exists(BASEMESH_PATH):
        raise FileNotFoundError(f"Base mesh not found: {BASEMESH_PATH}\nRun generate_basemesh_v4.py first!")

    objects = import_from_blend(BASEMESH_PATH)

    # Find the base mesh object
    basemesh = None
    for obj in objects:
        if "PenitentMechanism_Base" in obj.name or "BaseMesh" in obj.name:
            basemesh = obj
            break

    if not basemesh:
        # If no specific name found, use first mesh
        for obj in objects:
            if obj.type == 'MESH':
                basemesh = obj
                basemesh.name = "PenitentMechanism_Base"
                break

    if not basemesh:
        raise RuntimeError("Failed to import base mesh!")

    print(f"  ✓ Base mesh: {basemesh.name} ({len(basemesh.data.vertices)} verts)")
    return basemesh

def import_kitbash_asset(filename, target_location=None, target_rotation=None, parent=None):
    """
    Import a kitbash asset and optionally position/parent it.
    Returns list of imported objects.
    """
    filepath = os.path.join(KITBASH_DIR, filename)

    if not os.path.exists(filepath):
        print(f"  ⚠ WARNING: Kitbash asset not found: {filepath}")
        print(f"    Run generate_kitbash_assets.py first!")
        return []

    objects = import_from_blend(filepath)

    # Position and parent all imported objects
    for obj in objects:
        if target_location:
            obj.location = target_location
        if target_rotation:
            obj.rotation_euler = target_rotation
        if parent:
            obj.parent = parent

    return objects

# ============================================================================
# MULTI-LAYER PROCEDURAL MATERIALS (Same as V3)
# ============================================================================

def create_material_bronze_v3():
    """Advanced bronze material with verdigris and weathering"""
    mat = bpy.data.materials.new(name="MAT_Bronze_V3")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)

    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    bsdf.inputs['Metallic'].default_value = 0.95
    bsdf.inputs['Roughness'].default_value = 0.55

    # Layer 1: Base bronze
    noise_base = nodes.new('ShaderNodeTexNoise')
    noise_base.location = (-600, 200)
    noise_base.inputs['Scale'].default_value = 12.0
    noise_base.inputs['Detail'].default_value = 3.0

    ramp_base = nodes.new('ShaderNodeValToRGB')
    ramp_base.location = (-300, 200)
    ramp_base.color_ramp.elements[0].color = (0.12, 0.08, 0.05, 1.0)
    ramp_base.color_ramp.elements[1].color = (0.22, 0.16, 0.09, 1.0)

    # Layer 2: Verdigris
    noise_verdigris = nodes.new('ShaderNodeTexNoise')
    noise_verdigris.location = (-600, -100)
    noise_verdigris.inputs['Scale'].default_value = 6.0
    noise_verdigris.inputs['Detail'].default_value = 2.0

    ramp_verdigris = nodes.new('ShaderNodeValToRGB')
    ramp_verdigris.location = (-300, -100)
    ramp_verdigris.color_ramp.elements[0].position = 0.45
    ramp_verdigris.color_ramp.elements[0].color = (0, 0, 0, 1)
    ramp_verdigris.color_ramp.elements[1].color = (0.1, 0.3, 0.2, 1)

    # Layer 3: Dirt
    noise_dirt = nodes.new('ShaderNodeTexNoise')
    noise_dirt.location = (-600, -400)
    noise_dirt.inputs['Scale'].default_value = 20.0
    noise_dirt.inputs['Detail'].default_value = 5.0

    ramp_dirt = nodes.new('ShaderNodeValToRGB')
    ramp_dirt.location = (-300, -400)
    ramp_dirt.color_ramp.elements[0].position = 0.6
    ramp_dirt.color_ramp.elements[0].color = (0, 0, 0, 1)
    ramp_dirt.color_ramp.elements[1].color = (0.05, 0.04, 0.03, 1)

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
    map_range_rough.inputs['To Min'].default_value = 0.45
    map_range_rough.inputs['To Max'].default_value = 0.75

    # Connect
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
    """Ivory material with subtle variation"""
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

    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-400, 0)
    noise.inputs['Scale'].default_value = 18.0
    noise.inputs['Detail'].default_value = 2.0

    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (-200, 0)
    ramp.color_ramp.elements[0].color = (0.85, 0.82, 0.75, 1.0)
    ramp.color_ramp.elements[1].color = (0.92, 0.90, 0.85, 1.0)

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
    """Warm brass material"""
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

    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-400, 0)
    noise.inputs['Scale'].default_value = 15.0

    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (-200, 0)
    ramp.color_ramp.elements[0].color = (0.65, 0.45, 0.15, 1.0)
    ramp.color_ramp.elements[1].color = (0.80, 0.60, 0.25, 1.0)

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
    """Emission material for glow points"""
    mat = bpy.data.materials.new(name="MAT_Amber_Glow_V3")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (200, 0)

    emission = nodes.new('ShaderNodeEmission')
    emission.location = (0, 0)
    emission.inputs['Color'].default_value = (1.0, 0.6, 0.2, 1.0)
    emission.inputs['Strength'].default_value = 3.0

    links.new(emission.outputs['Emission'], output.inputs['Surface'])

    return mat

def assign_materials_to_objects(objects, material_map):
    """
    Assign materials to objects based on name patterns.
    material_map: dict of {name_pattern: material}
    """
    print("Assigning materials to objects...")

    for obj in objects:
        if obj.type != 'MESH':
            continue

        # Match object name to material
        assigned = False
        for pattern, material in material_map.items():
            if pattern.lower() in obj.name.lower():
                if not obj.data.materials:
                    obj.data.materials.append(material)
                else:
                    obj.data.materials[0] = material
                assigned = True
                print(f"  {obj.name} → {material.name}")
                break

        # Default material if no match
        if not assigned and not obj.data.materials:
            obj.data.materials.append(material_map.get('default'))
            print(f"  {obj.name} → (default)")

# ============================================================================
# RIGGING
# ============================================================================

def create_rigify_metarig():
    """Create Rigify metarig for humanoid"""
    print("Creating Rigify metarig...")

    try:
        bpy.ops.preferences.addon_enable(module='rigify')
    except:
        print("  ⚠ WARNING: Rigify addon not available")
        return None

    try:
        bpy.ops.object.armature_human_metarig_add()
        metarig = bpy.context.active_object
        metarig.name = "Penitent_MetaRig"
        metarig.location = (0, 0, 0)
        metarig.scale = (0.85, 0.85, 0.90)
        bpy.ops.object.transform_apply(scale=True)
        return metarig
    except:
        print("  ⚠ WARNING: Failed to create Rigify metarig")
        return None

def generate_rigify_rig(metarig):
    """Generate final rig from metarig"""
    if not metarig:
        return None

    print("Generating Rigify rig...")

    try:
        bpy.context.view_layer.objects.active = metarig
        bpy.ops.pose.rigify_generate()

        for obj in bpy.data.objects:
            if "rig" in obj.name.lower() and obj.type == 'ARMATURE' and obj != metarig:
                print(f"  ✓ Generated rig: {obj.name}")
                return obj
    except:
        print("  ⚠ WARNING: Rigify generation failed")

    return None

def apply_automatic_weights(mesh_objects, armature):
    """Apply automatic skinning weights"""
    if not armature:
        print("  Skipping weights - no armature")
        return

    print("Applying automatic weights...")

    for obj in mesh_objects:
        if obj.type != 'MESH':
            continue

        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        armature.select_set(True)
        bpy.context.view_layer.objects.active = armature

        try:
            bpy.ops.object.parent_set(type='ARMATURE_AUTO')
            print(f"  ✓ Weighted: {obj.name}")
        except:
            print(f"  ⚠ WARNING: Failed to weight {obj.name}")

# ============================================================================
# MAIN PIPELINE
# ============================================================================

def main():
    """Main avatar generation pipeline - V4 Architecture (TRUE KITBASHING)"""
    import sys

    print("=" * 60)
    print("THE PENITENT MECHANISM - Avatar Generator V4.0")
    print("TRUE KITBASHING: Imports pre-modeled assets, NO primitives")
    print("=" * 60)
    print(f"Blender: {bpy.app.version_string}")
    print(f"Python: {sys.version}")
    print("=" * 60)
    print()

    try:
        all_objects = []

        # STEP 1: Clear and import base mesh
        print("STEP 1: Importing base humanoid mesh...")
        clear_scene()
        basemesh = import_basemesh()
        all_objects.append(basemesh)
        print()

        # STEP 2: Import kitbash assets
        print("STEP 2: Importing kitbash assets...")

        # Halo (positioned above head)
        print("  → Mechanical Halo...")
        halo_objects = import_kitbash_asset(
            "Mech_Halo_01.blend",
            target_location=Vector((0, 0.10, 1.90)),
            target_rotation=Euler((math.radians(15), 0, 0)),
            parent=basemesh
        )
        all_objects.extend(halo_objects)

        # Shoulder mechanism (right shoulder)
        print("  → Shoulder Mechanism...")
        shoulder_objects = import_kitbash_asset(
            "Mech_Shoulder_01.blend",
            target_location=Vector((0.42, 0.05, 1.20)),
            parent=basemesh
        )
        all_objects.extend(shoulder_objects)

        # Blade hands (both sides)
        print("  → Left Blade Hand...")
        bladel_objects = import_kitbash_asset(
            "BladeHand_01.blend",
            target_location=Vector((0.54, 0.35, 0.70)),
            target_rotation=Euler((math.radians(-30), 0, math.radians(10))),
            parent=basemesh
        )
        all_objects.extend(bladel_objects)

        print("  → Right Blade Hand...")
        blader_objects = import_kitbash_asset(
            "BladeHand_01.blend",
            target_location=Vector((-0.54, 0.35, 0.70)),
            target_rotation=Euler((math.radians(-30), 0, math.radians(-10))),
            parent=basemesh
        )
        all_objects.extend(blader_objects)

        # Cable cluster (shoulder to back)
        print("  → Cable Cluster...")
        cable_objects = import_kitbash_asset(
            "CableCluster_01.blend",
            target_location=Vector((0.25, -0.10, 1.10)),
            parent=basemesh
        )
        all_objects.extend(cable_objects)

        print()

        # STEP 3: Create materials
        print("STEP 3: Creating multi-layer procedural materials...")
        mat_bronze = create_material_bronze_v3()
        mat_ivory = create_material_ivory_v3()
        mat_saffron = create_material_saffron_bronze_v3()
        mat_amber = create_material_amber_glow_v3()
        print("  ✓ 4 materials created")
        print()

        # STEP 4: Assign materials
        print("STEP 4: Assigning materials...")
        material_map = {
            'base': mat_ivory,
            'penitent': mat_ivory,
            'halo': mat_bronze,
            'shoulder': mat_bronze,
            'gear': mat_bronze,
            'piston': mat_saffron,
            'blade': mat_saffron,
            'palm': mat_bronze,
            'cable': mat_bronze,
            'glow': mat_amber,
            'default': mat_ivory,
        }
        assign_materials_to_objects(all_objects, material_map)
        print()

        # STEP 5: Setup rigging
        print("STEP 5: Setting up rigging...")
        metarig = create_rigify_metarig()
        rig = generate_rigify_rig(metarig)

        if rig:
            mesh_objects = [obj for obj in all_objects
                          if obj.type == 'MESH' and not obj.name.startswith('WGT-')]
            apply_automatic_weights(mesh_objects, rig)
        print()

        # STEP 6: Final statistics
        print("=" * 60)
        print("SCENE STATISTICS")
        print("=" * 60)

        mesh_objects = [obj for obj in all_objects if obj.type == 'MESH']
        total_verts = sum(len(obj.data.vertices) for obj in mesh_objects)
        total_faces = sum(len(obj.data.polygons) for obj in mesh_objects)

        print(f"  Total vertices: {total_verts}")
        print(f"  Total faces: {total_faces}")
        print(f"  Estimated triangles: {total_faces * 2}")
        print(f"  Mesh objects: {len(mesh_objects)}")
        print(f"  Materials: {len(bpy.data.materials)}")
        print("=" * 60)
        print()

        # STEP 7: Save
        print(f"Saving to: {OUTPUT_PATH}")
        bpy.ops.wm.save_as_mainfile(filepath=OUTPUT_PATH)
        print("✓ File saved!")
        print()

        print("=" * 60)
        print("✓ AVATAR GENERATION COMPLETE (V4 TRUE KITBASHING)!")
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
