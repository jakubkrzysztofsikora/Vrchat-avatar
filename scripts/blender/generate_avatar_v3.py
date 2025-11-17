#!/usr/bin/env python3
"""
The Penitent Mechanism - Avatar Generator V3.0
Complete architectural refactor using base mesh approach

ARCHITECTURE CHANGE:
- V1/V2: Built entire character from UV spheres and cylinders (snowman result)
- V3: Imports sculpted base mesh, then adds mechanical details via kitbashing

This produces proper character topology instead of stacked primitives.
"""

import bpy
import bmesh
import math
import os
import random
from mathutils import Vector, Euler

# Paths
BASEMESH_PATH = os.path.abspath("Avatar/BaseMeshes/PenitentMechanism_Base.blend")
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
# MECHANICAL KITBASH (primitives for mech parts only)
# ============================================================================

def add_shoulder_mechanism(base_mesh):
    """Add mechanical shoulder plating (right side)"""
    print("Adding shoulder mechanism...")

    # Main shoulder plate
    bpy.ops.mesh.primitive_cube_add(
        size=0.25,
        location=(0.42, 0.05, 1.20)
    )
    plate = bpy.context.active_object
    plate.name = "ShoulderPlate_Main"
    plate.scale = (1.0, 0.8, 0.6)
    bpy.ops.object.transform_apply(scale=True)

    # Add bevel for mechanical look
    bevel = plate.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.01
    bevel.segments = 3

    # Gear 1
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8,
        radius=0.08,
        depth=0.04,
        location=(0.50, 0.10, 1.25)
    )
    gear1 = bpy.context.active_object
    gear1.name = "Gear_1"
    gear1.rotation_euler = (0, math.radians(90), 0)

    # Gear 2
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8,
        radius=0.06,
        depth=0.03,
        location=(0.48, -0.05, 1.15)
    )
    gear2 = bpy.context.active_object
    gear2.name = "Gear_2"

    # Pistons
    for i, z_offset in enumerate([0.05, -0.05]):
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=6,
            radius=0.02,
            depth=0.12,
            location=(0.45, z_offset, 1.10)
        )
        piston = bpy.context.active_object
        piston.name = f"Piston_{i+1}"
        piston.rotation_euler = (math.radians(90), 0, 0)

    # Parent all to base mesh
    for obj in [plate, gear1, gear2]:
        obj.parent = base_mesh

    return [plate, gear1, gear2]

def add_mechanical_halo(base_mesh):
    """Create floating halo with bronze rings"""
    print("Creating mechanical halo...")

    # Main ring
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.40,
        minor_radius=0.015,
        major_segments=32,
        minor_segments=12,
        location=(0, 0.10, 1.90)
    )
    ring_main = bpy.context.active_object
    ring_main.name = "Halo_Ring_Main"
    ring_main.rotation_euler = (math.radians(15), 0, 0)

    # Inner ring
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.30,
        minor_radius=0.010,
        major_segments=24,
        minor_segments=8,
        location=(0, 0.10, 1.90)
    )
    ring_inner = bpy.context.active_object
    ring_inner.name = "Halo_Ring_Inner"
    ring_inner.rotation_euler = (math.radians(20), 0, math.radians(30))

    # Outer ring
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.50,
        minor_radius=0.012,
        major_segments=40,
        minor_segments=10,
        location=(0, 0.10, 1.90)
    )
    ring_outer = bpy.context.active_object
    ring_outer.name = "Halo_Ring_Outer"
    ring_outer.rotation_euler = (math.radians(10), 0, math.radians(-20))

    # Add amber glow spheres
    for i in range(6):
        angle = (i / 6.0) * 2 * math.pi
        x = 0.35 * math.cos(angle)
        y = 0.10 + 0.35 * math.sin(angle)

        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=8,
            ring_count=6,
            radius=0.025,
            location=(x, y, 1.90)
        )
        glow = bpy.context.active_object
        glow.name = f"Halo_Glow_{i}"

    # Parent to base mesh
    for obj in [ring_main, ring_inner, ring_outer]:
        obj.parent = base_mesh

    return [ring_main, ring_inner, ring_outer]

def add_blade_hands(base_mesh):
    """Replace hand stubs with fused blade-hands"""
    print("Creating blade-hands...")

    for side in ['L', 'R']:
        sign = 1 if side == 'L' else -1

        # Find and hide original hand
        for obj in bpy.data.objects:
            if f"Hand_{side}" in obj.name:
                obj.hide_render = True
                obj.hide_viewport = True

        # Create blade hand
        bpy.ops.mesh.primitive_cone_add(
            vertices=6,
            radius1=0.06,
            radius2=0.005,
            depth=0.25,
            location=(sign * 0.52, 0.40, 0.70),
            rotation=(math.radians(-30), 0, math.radians(sign * 10))
        )
        blade = bpy.context.active_object
        blade.name = f"Hand_Blade_{side}"

        # Add sharp edge
        bevel = blade.modifiers.new(name="Bevel", type='BEVEL')
        bevel.width = 0.002
        bevel.segments = 2

        blade.parent = base_mesh

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
    print("THE PENITENT MECHANISM - Avatar Generator V3.0")
    print("Architecture: Base Mesh + Kitbashing (NOT primitive stacking)")
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
        print()

        # STEP 2: Create upgraded materials
        print("STEP 2: Creating multi-layer procedural materials...")
        mat_bronze = create_material_bronze_v3()
        mat_ivory = create_material_ivory_v3()
        mat_saffron = create_material_saffron_bronze_v3()
        mat_amber = create_material_amber_glow_v3()
        print("  ✓ 4 materials created with procedural detail")
        print()

        # STEP 3: Assign base materials to body
        print("STEP 3: Assigning materials to base mesh...")
        if not basemesh.data.materials:
            basemesh.data.materials.append(mat_ivory)
        else:
            basemesh.data.materials[0] = mat_ivory
        print("  ✓ Base mesh materialed")
        print()

        # STEP 4: Add geometric detail
        print("STEP 4: Adding geometric detail...")
        add_panel_lines(basemesh, num_lines=8)
        add_bolts_to_object(basemesh, count=12)
        add_surface_weathering(basemesh)
        print()

        # STEP 5: Add mechanical kitbash
        print("STEP 5: Adding mechanical corruption...")
        shoulder_parts = add_shoulder_mechanism(basemesh)
        for part in shoulder_parts:
            if not part.data.materials:
                part.data.materials.append(mat_bronze)
        print()

        # STEP 6: Add halo
        print("STEP 6: Creating mechanical halo...")
        halo_parts = add_mechanical_halo(basemesh)
        for part in halo_parts:
            if not part.data.materials:
                part.data.materials.append(mat_bronze)
        print()

        # STEP 7: Add blade hands
        print("STEP 7: Creating blade-hands...")
        add_blade_hands(basemesh)
        print()

        # STEP 8: Setup rigging
        print("STEP 8: Setting up rigging...")
        metarig = create_rigify_metarig()
        rig = generate_rigify_rig(metarig)

        if rig:
            # Collect mesh objects (exclude Rigify widget objects)
            mesh_objects = [obj for obj in bpy.data.objects
                          if obj.type == 'MESH' and not obj.name.startswith('WGT-')]
            apply_automatic_weights(mesh_objects, rig)
        print()

        # STEP 9: Final statistics
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

        # STEP 10: Save
        print(f"Saving to: {OUTPUT_PATH}")
        bpy.ops.wm.save_as_mainfile(filepath=OUTPUT_PATH)
        print("✓ File saved!")
        print()

        print("=" * 60)
        print("✓ AVATAR GENERATION COMPLETE (V3 ARCHITECTURE)!")
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
