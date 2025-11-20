#!/usr/bin/env python3
"""
Texture Baking Script for The Penitent Mechanism
Bakes all materials to PBR texture maps for VRChat/Unity export
"""

import bpy
import os
import sys

# Configuration
CI_MODE = os.environ.get('CI', 'false').lower() == 'true'
TEXTURE_RESOLUTION = 1024 if CI_MODE else 2048
BAKE_SAMPLES = 32 if CI_MODE else 64

OUTPUT_DIR = os.path.abspath("Avatar/Textures")

# Standard PBR channels to bake
BAKE_CHANNELS = [
    ('DIFFUSE', 'BaseColor'),
    ('ROUGHNESS', 'Roughness'),
    ('EMIT', 'Emission'),
]


def setup_baking():
    """Setup scene for baking"""
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.device = 'CPU'
    bpy.context.scene.cycles.samples = BAKE_SAMPLES
    print(f"  Render engine: CYCLES")
    print(f"  Samples: {BAKE_SAMPLES}")


def create_bake_image(name, resolution=TEXTURE_RESOLUTION):
    """Create image for baking"""
    img = bpy.data.images.new(name, width=resolution, height=resolution, alpha=True)
    img.filepath_raw = os.path.join(OUTPUT_DIR, f"{name}.png")
    img.file_format = 'PNG'
    return img


def unwrap_mesh(obj):
    """Create UV map for object"""
    print(f"    Unwrapping {obj.name}...")

    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66, island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')


def bake_channel(obj, bake_type, image_name):
    """Bake a specific channel for an object"""
    print(f"    Baking {bake_type}...")

    # Create image
    img = create_bake_image(f"{obj.name}_{image_name}")

    # Get material
    if not obj.data.materials:
        print(f"      Skipping: no material")
        return None

    mat = obj.data.materials[0]
    if not mat.use_nodes:
        mat.use_nodes = True

    nodes = mat.node_tree.nodes

    # Add image texture node for baking target
    img_node = nodes.new(type='ShaderNodeTexImage')
    img_node.image = img
    nodes.active = img_node

    # Select object
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    # Bake settings
    bpy.context.scene.render.bake.use_pass_direct = False
    bpy.context.scene.render.bake.use_pass_indirect = False

    if bake_type == 'DIFFUSE':
        bpy.context.scene.render.bake.use_pass_color = True

    try:
        bpy.ops.object.bake(type=bake_type)
        img.save()
        print(f"      Saved: {img.filepath_raw}")
        return img
    except RuntimeError as e:
        print(f"      Failed: {e}")
        return None
    finally:
        # Clean up
        nodes.remove(img_node)


def bake_all_textures():
    """Bake textures for all mesh objects"""
    print("Starting texture baking...")
    print(f"  Resolution: {TEXTURE_RESOLUTION}x{TEXTURE_RESOLUTION}")
    print(f"  Output: {OUTPUT_DIR}")
    print("")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Get all mesh objects (exclude rig widgets)
    view_layer = bpy.context.view_layer
    mesh_objects = []
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and not obj.name.startswith('WGT-'):
            if obj.name in view_layer.objects:
                mesh_objects.append(obj)

    print(f"Found {len(mesh_objects)} mesh objects to bake")
    print("")

    total_baked = 0

    for obj in mesh_objects:
        print(f"Processing: {obj.name}")

        # Ensure UV map exists
        if not obj.data.uv_layers:
            unwrap_mesh(obj)

        # Bake all channels
        for bake_type, channel_name in BAKE_CHANNELS:
            result = bake_channel(obj, bake_type, channel_name)
            if result:
                total_baked += 1

        print("")

    print(f"Texture baking complete!")
    print(f"  Total textures: {total_baked}")


def create_vrchat_materials():
    """Create VRChat-compatible materials with baked textures"""
    print("Creating VRChat materials...")

    view_layer = bpy.context.view_layer
    materials_created = 0

    for obj in bpy.data.objects:
        if obj.type != 'MESH':
            continue
        if obj.name.startswith('WGT-'):
            continue
        if obj.name not in view_layer.objects:
            continue

        # Check if textures exist for this object
        base_color_path = os.path.join(OUTPUT_DIR, f"{obj.name}_BaseColor.png")
        if not os.path.exists(base_color_path):
            print(f"  Skipping {obj.name}: no baked textures")
            continue

        # Create new material
        mat_name = f"{obj.name}_VRChat"
        if mat_name in bpy.data.materials:
            mat = bpy.data.materials[mat_name]
        else:
            mat = bpy.data.materials.new(name=mat_name)

        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        nodes.clear()

        # Create Principled BSDF
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.location = (0, 0)

        # Create output
        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (300, 0)

        mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

        # Add texture nodes
        y_offset = 300

        texture_maps = [
            ('BaseColor', 'Base Color'),
            ('Roughness', 'Roughness'),
            ('Emission', 'Emission Color'),
        ]

        for tex_name, socket_name in texture_maps:
            img_path = os.path.join(OUTPUT_DIR, f"{obj.name}_{tex_name}.png")

            if os.path.exists(img_path):
                tex_node = nodes.new(type='ShaderNodeTexImage')
                tex_node.location = (-400, y_offset)
                tex_node.image = bpy.data.images.load(img_path)

                # Set colorspace
                if tex_name == 'Roughness':
                    tex_node.image.colorspace_settings.name = 'Non-Color'

                # Connect to BSDF
                mat.node_tree.links.new(tex_node.outputs['Color'], bsdf.inputs[socket_name])

                y_offset -= 300

        # Assign material
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)

        materials_created += 1

    print(f"  Created {materials_created} VRChat materials")


def main():
    """Main baking pipeline"""
    print("=" * 60)
    print("TEXTURE BAKING PIPELINE")
    print("=" * 60)
    print(f"Blender version: {bpy.app.version_string}")
    print(f"Mode: {'CI' if CI_MODE else 'Local'}")
    print("=" * 60 + "\n")

    try:
        # Load avatar
        blend_file = os.path.abspath("Avatar/PenitentMechanism.blend")
        print(f"Loading: {blend_file}")

        if not os.path.exists(blend_file):
            print(f"ERROR: File not found!")
            sys.exit(1)

        bpy.ops.wm.open_mainfile(filepath=blend_file)
        print("Loaded successfully\n")

        # Setup
        print("Setting up baking...")
        setup_baking()
        print("")

        # Bake textures
        bake_all_textures()
        print("")

        # Create materials
        create_vrchat_materials()
        print("")

        # Summary
        if os.path.exists(OUTPUT_DIR):
            texture_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.png')]
            total_size = sum(os.path.getsize(os.path.join(OUTPUT_DIR, f)) for f in texture_files)
            print(f"Created {len(texture_files)} textures ({total_size / (1024*1024):.2f} MB)")

        # Save
        print(f"\nSaving: {blend_file}")
        bpy.ops.wm.save_as_mainfile(filepath=blend_file)

        print("\n" + "=" * 60)
        print("TEXTURE BAKING COMPLETE")
        print("=" * 60)

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
