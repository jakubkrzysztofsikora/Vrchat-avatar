#!/usr/bin/env python3
"""
The Forgotten Architect - Procedural VRChat Avatar Generator
Generates a horror avatar blending Dwemer mechanical aesthetics with organic corruption.

Concept: Male, tall, biomechanical fusion - half elegant humanoid, half corrupted machine.
Elder Scrolls (Dwemer) + Lovecraftian + Asian horror aesthetics.
"""

import bpy
import bmesh
import math
import mathutils
import random
from mathutils import Vector, Matrix

# Configuration
AVATAR_HEIGHT = 2.1  # Tall male
SEED = 42
random.seed(SEED)

def clear_scene():
    """Remove default objects"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def create_base_body():
    """Create base humanoid body using meta-rig for Rigify"""
    print("Creating base humanoid meta-rig...")

    # Add Rigify meta-rig (basic human)
    bpy.ops.object.armature_basic_human_metarig_add()
    metarig = bpy.context.active_object
    metarig.name = "ForgottenArchitect_MetaRig"

    # Scale to tall male proportions
    metarig.scale = (1.0, 1.0, AVATAR_HEIGHT / 1.7)
    bpy.ops.object.transform_apply(scale=True)

    return metarig

def create_body_mesh():
    """Create the body mesh with asymmetric mechanical corruption"""
    print("Generating body mesh...")

    # Create base mesh from cube (will be subdivided and sculpted)
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1.0))
    body = bpy.context.active_object
    body.name = "Body"

    # Enter edit mode and create basic humanoid shape
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')

    # Subdivide for detail
    bpy.ops.mesh.subdivide(number_cuts=5)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Add subdivision surface for smooth organic areas
    subdiv = body.modifiers.new(name="Subdivision", type='SUBSURF')
    subdiv.levels = 2
    subdiv.render_levels = 3

    # Sculpt basic humanoid proportions using proportional editing
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(body.data)

    # Simple humanoid shape (this is a simplified version - Rigify will handle the rest)
    # We'll let the skinning handle most of the body deformation

    bpy.ops.object.mode_set(mode='OBJECT')

    return body

def create_mechanical_asymmetry(body):
    """Add Dwemer-style mechanical plating to half of the body"""
    print("Adding mechanical corruption...")

    # Create mechanical plating on right side
    bpy.ops.mesh.primitive_cube_add(size=0.3, location=(0.4, 0, 1.5))
    plate = bpy.context.active_object
    plate.name = "ChestPlate_Right"

    # Add array modifier for segmented plating
    array_mod = plate.modifiers.new(name="Array", type='ARRAY')
    array_mod.count = 3
    array_mod.relative_offset_displace[0] = 0
    array_mod.relative_offset_displace[2] = 1.2

    # Add bevel for mechanical edges
    bevel = plate.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.01
    bevel.segments = 2

    # Create shoulder mechanism (right side only - asymmetric)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.4,
                                        location=(0.6, 0, 1.6),
                                        rotation=(0, math.pi/2, 0))
    shoulder_mech = bpy.context.active_object
    shoulder_mech.name = "ShoulderMechanism_Right"

    # Oxidized bronze material
    create_bronze_material(plate)
    create_bronze_material(shoulder_mech)

    return [plate, shoulder_mech]

def create_head():
    """Create head with half-masked face (bronze plate covering right side)"""
    print("Creating head with asymmetric plating...")

    # Base head - UV sphere
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.16, location=(0, 0, 1.85))
    head = bpy.context.active_object
    head.name = "Head"

    # Slight scaling for male proportions
    head.scale = (0.9, 0.85, 1.0)
    bpy.ops.object.transform_apply(scale=True)

    # Subdivision for smooth skin
    subdiv = head.modifiers.new(name="Subdivision", type='SUBSURF')
    subdiv.levels = 3

    # Create face plate (right side)
    bpy.ops.mesh.primitive_cube_add(size=0.18, location=(0.09, -0.08, 1.85))
    face_plate = bpy.context.active_object
    face_plate.name = "FacePlate_Right"
    face_plate.scale = (0.8, 1.0, 1.2)
    bpy.ops.object.transform_apply(scale=True)

    # Boolean modifier to embed plate into face
    bool_mod = head.modifiers.new(name="FacePlate", type='BOOLEAN')
    bool_mod.operation = 'UNION'
    bool_mod.object = face_plate

    # Mechanical eye (right side) - multiple lenses
    for i in range(3):
        angle = (i - 1) * 0.3
        offset_y = math.sin(angle) * 0.08
        offset_z = math.cos(angle) * 0.08

        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.015 - (i * 0.003),
            depth=0.05,
            location=(0.12, -0.1 + offset_y, 1.85 + offset_z),
            rotation=(0, math.pi/2, angle)
        )
        lens = bpy.context.active_object
        lens.name = f"MechanicalEye_Lens{i}"
        create_glass_material(lens, emit_color=(1.0, 0.6, 0.2, 1.0))  # Amber glow

    create_bronze_material(face_plate)
    create_skin_material(head)

    return head

def create_hair_tendrils():
    """Create hair that transitions into metallic cable-tendrils"""
    print("Creating hair-to-cable corruption...")

    tendrils = []
    num_tendrils = 12

    for i in range(num_tendrils):
        # Create curve for each tendril
        angle = (i / num_tendrils) * 2 * math.pi
        radius = 0.14

        x = math.cos(angle) * radius
        y = math.sin(angle) * radius

        # Create bezier curve
        curve_data = bpy.data.curves.new(name=f"Tendril_{i}", type='CURVE')
        curve_data.dimensions = '3D'
        curve_data.fill_mode = 'FULL'
        curve_data.bevel_depth = 0.008 if i < 8 else 0.003  # Thicker for front tendrils
        curve_data.bevel_resolution = 3

        # Create spline
        spline = curve_data.splines.new('BEZIER')
        spline.bezier_points.add(4)  # 5 points total

        # Define points (head -> down to back, with some sway)
        points_positions = [
            (x, y, 1.88),  # Head origin
            (x * 1.2, y * 1.2 - 0.1, 1.7),  # Flow down
            (x * 1.1, y * 1.1 - 0.3, 1.4),  # Continue down
            (x * 0.9, y * 0.9 - 0.5, 1.0),  # Flow back
            (x * 0.7, y * 0.7 - 0.7, 0.6),  # End low
        ]

        for idx, pos in enumerate(points_positions):
            point = spline.bezier_points[idx]
            point.co = pos
            point.handle_left_type = 'AUTO'
            point.handle_right_type = 'AUTO'

        # Create object from curve
        tendril_obj = bpy.data.objects.new(f"Tendril_{i}", curve_data)
        bpy.context.collection.objects.link(tendril_obj)
        tendrils.append(tendril_obj)

        # Material - transition from hair to metal
        if i < 8:
            create_hair_material(tendril_obj)
        else:
            create_cable_material(tendril_obj)

    return tendrils

def create_bronze_material(obj):
    """Oxidized bronze Dwemer material"""
    mat = bpy.data.materials.new(name="OxidizedBronze")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()

    # Principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    bsdf.inputs['Base Color'].default_value = (0.25, 0.15, 0.08, 1.0)  # Dark bronze
    bsdf.inputs['Metallic'].default_value = 0.9
    bsdf.inputs['Roughness'].default_value = 0.6

    # Add patina (green oxidation)
    mix_rgb = nodes.new(type='ShaderNodeMixRGB')
    mix_rgb.location = (-200, 0)
    mix_rgb.inputs['Color2'].default_value = (0.1, 0.3, 0.2, 1.0)  # Green patina
    mix_rgb.inputs['Fac'].default_value = 0.3

    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.location = (-400, 0)
    noise.inputs['Scale'].default_value = 5.0

    # Connect
    links = mat.node_tree.links
    links.new(noise.outputs['Fac'], mix_rgb.inputs['Fac'])
    links.new(mix_rgb.outputs['Color'], bsdf.inputs['Base Color'])

    # Output
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (200, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    obj.data.materials.append(mat)

def create_skin_material(obj):
    """Pale, uncanny skin material"""
    mat = bpy.data.materials.new(name="UncannyFlesh")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()

    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    bsdf.inputs['Base Color'].default_value = (0.85, 0.78, 0.72, 1.0)  # Pale skin
    bsdf.inputs['Subsurface'].default_value = 0.1
    bsdf.inputs['Subsurface Color'].default_value = (0.9, 0.6, 0.5, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.4

    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (200, 0)
    mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    obj.data.materials.append(mat)

def create_hair_material(obj):
    """Black hair material"""
    mat = bpy.data.materials.new(name="BlackHair")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()

    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.3
    bsdf.inputs['Sheen'].default_value = 0.5

    output = nodes.new(type='ShaderNodeOutputMaterial')
    mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    obj.data.materials.append(mat)

def create_cable_material(obj):
    """Metallic cable material"""
    mat = bpy.data.materials.new(name="MetalCable")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()

    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.15, 0.12, 0.10, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.95
    bsdf.inputs['Roughness'].default_value = 0.3

    output = nodes.new(type='ShaderNodeOutputMaterial')
    mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    obj.data.materials.append(mat)

def create_glass_material(obj, emit_color=(1, 1, 1, 1)):
    """Glass with emission (for mechanical eye lenses)"""
    mat = bpy.data.materials.new(name="EmissiveGlass")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()

    # Glass BSDF
    glass = nodes.new(type='ShaderNodeBsdfGlass')
    glass.location = (-100, 100)
    glass.inputs['IOR'].default_value = 1.45

    # Emission
    emission = nodes.new(type='ShaderNodeEmission')
    emission.location = (-100, -100)
    emission.inputs['Color'].default_value = emit_color
    emission.inputs['Strength'].default_value = 2.0

    # Mix
    mix = nodes.new(type='ShaderNodeMixShader')
    mix.location = (100, 0)
    mix.inputs['Fac'].default_value = 0.8

    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (300, 0)

    links = mat.node_tree.links
    links.new(glass.outputs['BSDF'], mix.inputs[1])
    links.new(emission.outputs['Emission'], mix.inputs[2])
    links.new(mix.outputs['Shader'], output.inputs['Surface'])

    obj.data.materials.append(mat)

def join_body_parts():
    """Join all mesh parts into single body mesh"""
    print("Joining body parts...")

    # Select all mesh objects
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and 'Tendril' not in obj.name:
            obj.select_set(True)

    # Set active object
    bpy.context.view_layer.objects.active = bpy.data.objects.get('Head')

    # Join (commented out for now - we want separate objects for easier rigging)
    # bpy.ops.object.join()

def setup_armature_and_rig():
    """Generate Rigify rig and bind mesh"""
    print("Setting up Rigify armature...")

    # Select meta-rig
    metarig = bpy.data.objects.get('ForgottenArchitect_MetaRig')
    if not metarig:
        print("Meta-rig not found, creating new one...")
        metarig = create_base_body()

    bpy.context.view_layer.objects.active = metarig
    metarig.select_set(True)

    # Generate Rigify rig
    # Note: Rigify must be enabled in Blender preferences
    try:
        bpy.ops.pose.rigify_generate()
        print("Rigify rig generated successfully")
        rig = bpy.context.active_object
        rig.name = "ForgottenArchitect_Rig"
    except Exception as e:
        print(f"Rigify generation failed: {e}")
        print("Using meta-rig as base armature")
        rig = metarig

    return rig

def apply_automatic_weights(rig):
    """Apply automatic skinning weights to mesh"""
    print("Applying automatic weights...")

    # Select mesh objects
    mesh_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH']

    for mesh_obj in mesh_objects:
        # Skip tendril curves
        if 'Tendril' in mesh_obj.name:
            continue

        mesh_obj.select_set(True)

    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig

    # Parent with automatic weights
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')

def main():
    """Main generation pipeline"""
    print("=" * 60)
    print("THE FORGOTTEN ARCHITECT - Procedural Avatar Generation")
    print("=" * 60)

    clear_scene()

    # Create base armature
    metarig = create_base_body()

    # Create body mesh
    body = create_body_mesh()

    # Create head with asymmetric plating
    head = create_head()

    # Create mechanical corruption
    mechanical_parts = create_mechanical_asymmetry(body)

    # Create hair-to-cable tendrils
    tendrils = create_hair_tendrils()

    # Setup rigging
    rig = setup_armature_and_rig()

    # Apply skinning
    apply_automatic_weights(rig)

    print("=" * 60)
    print("Avatar generation complete!")
    print("=" * 60)

    # Save file
    output_path = "/home/user/Vrchat-avatar/Avatar/ForgottenArchitect.blend"
    bpy.ops.wm.save_as_mainfile(filepath=output_path)
    print(f"Saved to: {output_path}")

if __name__ == "__main__":
    main()
