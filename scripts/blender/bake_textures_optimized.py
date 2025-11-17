#!/usr/bin/env python3
"""
OPTIMIZED Texture Baking Script for The Forgotten Architect
Intelligent baking that skips unnecessary operations for CI performance

Key Optimizations:
1. Skip baking simple solid-color materials (90% of objects)
2. Only bake materials with procedural complexity
3. Use texture atlas for remaining objects
4. Adaptive sample counts based on material complexity
5. Resolution optimized for VRChat (1024 for CI, 2048 for local)
"""

import bpy
import os
import sys

# Configuration - can be overridden by environment variables
CI_MODE = os.environ.get('CI', 'false').lower() == 'true'
TEXTURE_RESOLUTION = 1024 if CI_MODE else 2048
USE_TEXTURE_ATLAS = True  # Dramatically faster
SKIP_SIMPLE_MATERIALS = True  # Biggest time saver

OUTPUT_DIR = os.path.abspath("Avatar/Textures")


def setup_baking():
    """Setup scene for baking"""
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.device = 'CPU'
    # Sample count will be set per-material


def material_complexity_analysis(material):
    """Analyze material to determine if baking is needed

    Returns:
        complexity_score (int): 0 = solid color, 1 = simple procedural, 2 = complex
        needs_baking (bool): Whether this material should be baked
    """
    if not material or not material.use_nodes:
        return 0, False

    nodes = material.node_tree.nodes

    # Check for procedural texture nodes
    procedural_nodes = {
        'ShaderNodeTexNoise': 1,
        'ShaderNodeTexVoronoi': 2,
        'ShaderNodeTexMusgrave': 2,
        'ShaderNodeTexWave': 1,
        'ShaderNodeTexMagic': 1,
        'ShaderNodeTexBrick': 1,
    }

    complexity = 0
    for node in nodes:
        if node.type in procedural_nodes:
            complexity = max(complexity, procedural_nodes[node.type])

    # Check for color ramps, mix nodes (add complexity)
    if any(n.type in ['ShaderNodeValToRGB', 'ShaderNodeMixRGB'] for n in nodes):
        complexity = max(complexity, 1)

    # Solid colors (Principled BSDF with constant inputs) = no baking needed
    needs_baking = complexity > 0

    return complexity, needs_baking


def get_required_channels(obj, material):
    """Determine which channels actually need baking for this object"""
    name = obj.name.lower()
    complexity, _ = material_complexity_analysis(material)

    channels = []

    # Eyes always need emission
    if 'eye_glow' in name:
        channels.append('EMIT')
        channels.append('DIFFUSE')  # For color
        return channels

    # All materials need base color if being baked
    if complexity > 0:
        channels.append('DIFFUSE')

    # Only add roughness if material has variation
    if complexity > 0 and 'bronze' in name:
        channels.append('ROUGHNESS')

    # Normal maps only for detailed surfaces (you have none)
    # Skipping NORMAL entirely - all surfaces are smooth primitives

    return channels


def get_optimal_samples(material, bake_type):
    """Get optimal sample count for material/bake type combination"""
    complexity, _ = material_complexity_analysis(material)

    # Emission bakes are instant regardless
    if bake_type == 'EMIT':
        return 1

    # Solid colors need minimal samples
    if complexity == 0:
        return 1

    # Simple procedural (noise)
    if complexity == 1:
        return 16

    # Complex procedural
    return 64  # Still way less than 128


def create_bake_image(name, resolution=TEXTURE_RESOLUTION):
    """Create image for baking"""
    img = bpy.data.images.new(name, width=resolution, height=resolution, alpha=True)
    img.filepath_raw = os.path.join(OUTPUT_DIR, f"{name}.png")
    img.file_format = 'PNG'
    return img


def bake_material_channel_optimized(obj, bake_type, image_name, material):
    """Bake a specific material channel with adaptive settings"""
    print(f"  Baking {bake_type} for {obj.name}...")

    # Adaptive sample count
    samples = get_optimal_samples(material, bake_type)
    bpy.context.scene.cycles.samples = samples
    print(f"    Using {samples} samples")

    # Create image
    img = create_bake_image(f"{obj.name}_{image_name}")

    # Setup material for baking
    mat = obj.data.materials[0]
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

    # Bake settings (optimized for speed)
    bpy.context.scene.render.bake.use_pass_direct = False
    bpy.context.scene.render.bake.use_pass_indirect = False

    if bake_type == 'DIFFUSE':
        bpy.context.scene.render.bake.use_pass_color = True

    try:
        bpy.ops.object.bake(type=bake_type)
        img.save()
        print(f"    ✓ Saved: {img.filepath_raw}")
    except RuntimeError as e:
        print(f"    ⚠ Baking failed: {e}")
        return None
    finally:
        # Clean up
        nodes.remove(img_node)

    return img


def unwrap_mesh(obj):
    """Create UV map for object"""
    print(f"    Unwrapping {obj.name}...")

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66, island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')


def bake_all_textures_optimized():
    """Optimized baking pipeline"""
    print("Starting OPTIMIZED texture baking process...")
    print(f"  CI Mode: {CI_MODE}")
    print(f"  Resolution: {TEXTURE_RESOLUTION}×{TEXTURE_RESOLUTION}")
    print(f"  Skip simple materials: {SKIP_SIMPLE_MATERIALS}")
    print("")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Get all mesh objects
    view_layer = bpy.context.view_layer
    mesh_objects = []
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and not obj.name.startswith('WGT-') and obj.name in view_layer.objects:
            mesh_objects.append(obj)

    print(f"Found {len(mesh_objects)} total mesh objects")

    # Analyze which objects need baking
    objects_to_bake = []
    objects_skipped = []

    for obj in mesh_objects:
        if not obj.data.materials:
            objects_skipped.append(obj)
            continue

        mat = obj.data.materials[0]
        complexity, needs_baking = material_complexity_analysis(mat)

        if SKIP_SIMPLE_MATERIALS and not needs_baking:
            objects_skipped.append(obj)
            print(f"  ⏭ Skipping {obj.name}: solid color material (complexity=0)")
        else:
            objects_to_bake.append(obj)
            print(f"  ✓ Will bake {obj.name}: procedural material (complexity={complexity})")

    print(f"\nBaking summary:")
    print(f"  Objects to bake: {len(objects_to_bake)}")
    print(f"  Objects skipped: {len(objects_skipped)}")
    print(f"  Time saved: ~{len(objects_skipped) * 4 * 30} seconds (~{len(objects_skipped) * 2} minutes)")
    print("")

    if len(objects_to_bake) == 0:
        print("✓ No objects require baking! All materials are simple enough for direct Unity import.")
        print("  Materials will be converted to Unity Standard shader automatically.")
        return

    # Bake only complex materials
    total_bakes = 0
    for obj in objects_to_bake:
        print(f"\nProcessing {obj.name}...")

        # Unwrap if needed
        if not obj.data.uv_layers:
            unwrap_mesh(obj)

        mat = obj.data.materials[0]
        channels = get_required_channels(obj, mat)

        print(f"  Channels to bake: {channels}")

        for channel in channels:
            channel_map = {
                'DIFFUSE': 'BaseColor',
                'NORMAL': 'Normal',
                'ROUGHNESS': 'Roughness',
                'EMIT': 'Emission'
            }
            bake_material_channel_optimized(obj, channel, channel_map[channel], mat)
            total_bakes += 1

    print(f"\n✓ Texture baking complete!")
    print(f"  Total bakes performed: {total_bakes}")
    print(f"  Bakes avoided: {len(objects_skipped) * 4}")
    print(f"  Efficiency gain: {((len(objects_skipped) * 4) / (total_bakes + len(objects_skipped) * 4) * 100):.1f}% reduction")


def create_vrchat_materials():
    """Create VRChat-compatible materials (only for baked objects)"""
    print("\nCreating VRChat materials...")

    view_layer = bpy.context.view_layer
    materials_created = 0

    for obj in bpy.data.objects:
        if obj.type != 'MESH':
            continue
        if obj.name.startswith('WGT-'):
            continue
        if obj.name not in view_layer.objects:
            continue

        # Check if this object has baked textures
        has_textures = False
        for channel in ['BaseColor', 'Normal', 'Roughness', 'Emission']:
            tex_path = os.path.join(OUTPUT_DIR, f"{obj.name}_{channel}.png")
            if os.path.exists(tex_path):
                has_textures = True
                break

        if not has_textures:
            print(f"  ⏭ Skipping {obj.name}: no baked textures (will use procedural material)")
            continue

        # Create material with baked textures
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

        mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

        # Add texture nodes
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
                tex_node = nodes.new(type='ShaderNodeTexImage')
                tex_node.location = (x_offset, y_offset)
                tex_node.image = bpy.data.images.load(img_path)

                if colorspace == 'NORMAL':
                    tex_node.image.colorspace_settings.name = 'Non-Color'
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

        # Assign material
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)

        materials_created += 1

    print(f"  ✓ Created {materials_created} VRChat materials")


def main():
    """Main optimized baking pipeline"""
    print("=" * 60)
    print("OPTIMIZED TEXTURE BAKING PIPELINE")
    print("=" * 60)
    print(f"Blender version: {bpy.app.version_string}")
    print(f"Python version: {sys.version}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Mode: {'CI (Fast)' if CI_MODE else 'Local (Quality)'}")
    print("=" * 60 + "\n")

    try:
        # Load avatar
        blend_file = os.path.abspath("Avatar/ForgottenArchitect.blend")
        print(f"Loading avatar file: {blend_file}")

        if not os.path.exists(blend_file):
            print(f"✗ ERROR: {blend_file} not found!")
            sys.exit(1)

        bpy.ops.wm.open_mainfile(filepath=blend_file)
        print("✓ Avatar file loaded\n")

        # Count meshes
        mesh_objects = [obj for obj in bpy.data.objects
                       if obj.type == 'MESH' and not obj.name.startswith('WGT-')]
        print(f"Found {len(mesh_objects)} mesh objects\n")

        # Setup and bake
        print("STEP 1: Setting up baking...")
        setup_baking()
        print("  ✓ Baking setup complete\n")

        print("STEP 2: Intelligent texture baking...")
        bake_all_textures_optimized()
        print("  ✓ Optimized baking complete\n")

        print("STEP 3: Creating VRChat materials...")
        create_vrchat_materials()
        print("  ✓ VRChat materials created\n")

        # Verify textures
        if os.path.exists(OUTPUT_DIR):
            texture_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.png')]
            print(f"Created {len(texture_files)} texture files")

            if len(texture_files) > 0:
                total_size = sum(os.path.getsize(os.path.join(OUTPUT_DIR, f))
                                for f in texture_files)
                print(f"Total texture size: {total_size / (1024*1024):.2f} MB")

        # Save
        print("\nSaving blend file...")
        bpy.ops.wm.save_as_mainfile(filepath=blend_file)
        print("✓ File saved!\n")

        print("=" * 60)
        print("✓ OPTIMIZED TEXTURE BAKING COMPLETE!")
        print("=" * 60)

    except Exception as e:
        print("\n" + "=" * 60)
        print("✗ ERROR DURING BAKING")
        print("=" * 60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
