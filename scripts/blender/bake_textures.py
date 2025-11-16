#!/usr/bin/env python3
"""
Texture Baking Script for The Forgotten Architect
Bakes procedural materials to PBR texture maps (BaseColor, Normal, Metallic, Roughness, Emission)
"""

import bpy
import os

OUTPUT_DIR = os.path.abspath("Avatar/Textures")
TEXTURE_RESOLUTION = 2048

def setup_baking():
    """Setup scene for baking"""
    # Set render engine to Cycles for baking
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.device = 'CPU'
    bpy.context.scene.cycles.samples = 128  # Lower for faster CI builds

def unwrap_mesh(obj):
    """Create UV map for object"""
    print(f"Unwrapping {obj.name}...")

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # Enter edit mode
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')

    # Smart UV unwrap
    bpy.ops.uv.smart_project(angle_limit=66, island_margin=0.02)

    bpy.ops.object.mode_set(mode='OBJECT')

def create_bake_image(name, resolution=TEXTURE_RESOLUTION):
    """Create image for baking"""
    img = bpy.data.images.new(name, width=resolution, height=resolution, alpha=True)
    img.filepath_raw = os.path.join(OUTPUT_DIR, f"{name}.png")
    img.file_format = 'PNG'
    return img

def bake_material_channel(obj, bake_type, image_name):
    """Bake a specific material channel"""
    print(f"Baking {bake_type} for {obj.name}...")

    # Create image
    img = create_bake_image(f"{obj.name}_{image_name}")

    # Ensure object has a material
    if not obj.data.materials:
        # Create temporary material for baking
        temp_mat = bpy.data.materials.new(name=f"{obj.name}_BakeMat")
        obj.data.materials.append(temp_mat)

    mat = obj.data.materials[0]
    mat.use_nodes = True
    nodes = mat.node_tree.nodes

    # Add image texture node for baking target
    img_node = nodes.new(type='ShaderNodeTexImage')
    img_node.image = img
    nodes.active = img_node  # CRITICAL: Set as active for baking

    # Select object
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    # Bake settings
    bpy.context.scene.render.bake.use_pass_direct = False
    bpy.context.scene.render.bake.use_pass_indirect = False

    # Bake based on type
    if bake_type == 'DIFFUSE':
        bpy.context.scene.render.bake.use_pass_direct = False
        bpy.context.scene.render.bake.use_pass_indirect = False
        bpy.context.scene.render.bake.use_pass_color = True

    try:
        bpy.ops.object.bake(type=bake_type)
        # Save image
        img.save()
        print(f"✓ Saved: {img.filepath_raw}")
    except RuntimeError as e:
        print(f"⚠ Baking failed for {obj.name}: {e}")
        print(f"  Skipping {bake_type} channel")
        return None

    # Clean up: Remove the temporary image node
    nodes.remove(img_node)

    return img

def bake_all_textures():
    """Bake all PBR textures for all mesh objects"""
    print("Starting texture baking process...")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Get all mesh objects (excluding Rigify widgets)
    view_layer = bpy.context.view_layer
    mesh_objects = []
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and not obj.name.startswith('WGT-') and obj.name in view_layer.objects:
            mesh_objects.append(obj)

    print(f"Found {len(mesh_objects)} mesh objects to bake")

    for obj in mesh_objects:
        print(f"\nProcessing {obj.name}...")

        # Unwrap if needed
        if not obj.data.uv_layers:
            unwrap_mesh(obj)

        # Bake different channels
        bake_material_channel(obj, 'DIFFUSE', 'BaseColor')
        bake_material_channel(obj, 'NORMAL', 'Normal')
        bake_material_channel(obj, 'ROUGHNESS', 'Roughness')
        bake_material_channel(obj, 'EMIT', 'Emission')

        # Metallic (we'll use roughness and invert for non-metallic areas)
        # For VRChat, metallic is often packed with roughness

    print("\nTexture baking complete!")

def create_vrchat_materials():
    """Create VRChat-compatible materials using baked textures"""
    print("Creating VRChat materials...")

    view_layer = bpy.context.view_layer
    for obj in bpy.data.objects:
        if obj.type != 'MESH':
            continue

        # Skip Rigify widgets
        if obj.name.startswith('WGT-'):
            continue

        # Skip if not in view layer
        if obj.name not in view_layer.objects:
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

        # Principled BSDF
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.location = (0, 0)

        # Output
        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (300, 0)

        # Link BSDF to output
        mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

        # Add texture nodes (if they exist)
        x_offset = -400
        y_offset = 300

        texture_maps = [
            ('BaseColor', 'Base Color', 'COLOR'),
            ('Normal', 'Normal', 'NORMAL'),
            ('Roughness', 'Roughness', 'VALUE'),
            ('Emission', 'Emission', 'COLOR'),
        ]

        for tex_name, socket_name, colorspace in texture_maps:
            img_path = os.path.join(OUTPUT_DIR, f"{obj.name}_{tex_name}.png")

            if os.path.exists(img_path):
                # Create image texture node
                tex_node = nodes.new(type='ShaderNodeTexImage')
                tex_node.location = (x_offset, y_offset)
                tex_node.image = bpy.data.images.load(img_path)

                if colorspace == 'NORMAL':
                    tex_node.image.colorspace_settings.name = 'Non-Color'
                    # Add normal map node
                    normal_node = nodes.new(type='ShaderNodeNormalMap')
                    normal_node.location = (x_offset + 200, y_offset)
                    mat.node_tree.links.new(tex_node.outputs['Color'], normal_node.inputs['Color'])
                    mat.node_tree.links.new(normal_node.outputs['Normal'], bsdf.inputs['Normal'])
                elif colorspace == 'VALUE':
                    tex_node.image.colorspace_settings.name = 'Non-Color'
                    mat.node_tree.links.new(tex_node.outputs['Color'], bsdf.inputs[socket_name])
                else:
                    mat.node_tree.links.new(tex_node.outputs['Color'], bsdf.inputs[socket_name])

                y_offset -= 300

        # Assign material to object
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)

def main():
    """Main baking pipeline"""
    import sys

    print("=" * 60)
    print("TEXTURE BAKING PIPELINE")
    print("=" * 60)
    print(f"Blender version: {bpy.app.version_string}")
    print(f"Python version: {sys.version}")
    print(f"Output directory: {OUTPUT_DIR}")
    print("=" * 60 + "\n")

    try:
        # Load the generated avatar
        blend_file = os.path.abspath("Avatar/ForgottenArchitect.blend")
        print(f"Loading avatar file: {blend_file}")

        if not os.path.exists(blend_file):
            print(f"✗ ERROR: {blend_file} not found!")
            print("Make sure generate_avatar.py has been run first.")
            return

        file_size = os.path.getsize(blend_file)
        print(f"File size: {file_size / 1024:.1f} KB")

        if file_size < 10000:
            print("⚠ WARNING: Blend file is very small - may be corrupted or empty!")

        bpy.ops.wm.open_mainfile(filepath=blend_file)
        print("✓ Avatar file loaded\n")

        # Count mesh objects
        mesh_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH' and not obj.name.startswith('WGT-')]
        print(f"Found {len(mesh_objects)} mesh objects to bake")

        if len(mesh_objects) == 0:
            print("✗ ERROR: No mesh objects found in scene!")
            return

        print(f"Mesh objects: {[obj.name for obj in mesh_objects]}\n")

        # Setup and bake
        print("STEP 1: Setting up baking...")
        setup_baking()
        print("  ✓ Baking setup complete\n")

        print("STEP 2: Baking textures...")
        bake_all_textures()
        print("  ✓ Texture baking complete\n")

        print("STEP 3: Creating VRChat materials...")
        create_vrchat_materials()
        print("  ✓ VRChat materials created\n")

        # Verify textures were created
        if os.path.exists(OUTPUT_DIR):
            texture_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.png')]
            print(f"Created {len(texture_files)} texture files:")
            for tex_file in texture_files:
                tex_path = os.path.join(OUTPUT_DIR, tex_file)
                tex_size = os.path.getsize(tex_path) / 1024
                print(f"  - {tex_file} ({tex_size:.1f} KB)")

            if len(texture_files) == 0:
                print("⚠ WARNING: No texture files were created!")

        # Save with baked textures
        print("\nSaving blend file with baked textures...")
        bpy.ops.wm.save_as_mainfile(filepath=blend_file)
        print("✓ File saved successfully!")

        print("\n" + "=" * 60)
        print("✓ TEXTURE BAKING COMPLETE!")
        print("=" * 60)

    except Exception as e:
        print("\n" + "=" * 60)
        print("✗ FATAL ERROR DURING TEXTURE BAKING")
        print("=" * 60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 60)
        raise

if __name__ == "__main__":
    main()
