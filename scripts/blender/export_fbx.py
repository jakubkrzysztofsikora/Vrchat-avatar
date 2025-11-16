#!/usr/bin/env python3
"""
FBX Export Script for The Forgotten Architect
Exports the final avatar with all animations for Unity import
"""

import bpy
import os

OUTPUT_PATH = os.path.abspath("Avatar/ForgottenArchitect.fbx")

def prepare_for_export():
    """Prepare scene for Unity-compatible FBX export"""
    print("Preparing for FBX export...")

    # Get view layer
    view_layer = bpy.context.view_layer

    # Apply all modifiers except Armature
    for obj in bpy.data.objects:
        # Skip non-mesh objects
        if obj.type != 'MESH':
            continue

        # Skip Rigify widget objects
        if obj.name.startswith('WGT-'):
            continue

        # Skip if not in view layer
        if obj.name not in view_layer.objects:
            continue

        # Set as active and apply modifiers
        bpy.context.view_layer.objects.active = obj
        for modifier in obj.modifiers:
            if modifier.type != 'ARMATURE':
                try:
                    bpy.ops.object.modifier_apply(modifier=modifier.name)
                    try:
                        print(f"Applied modifier {modifier.name} on {obj.name}")
                    except UnicodeDecodeError:
                        print(f"Applied modifier on object (name contains non-ASCII chars)")
                except Exception as e:
                    try:
                        print(f"Could not apply modifier {modifier.name} on {obj.name}: {e}")
                    except UnicodeDecodeError:
                        print(f"Could not apply modifier on object (encoding error): {e}")

def export_to_fbx():
    """Export scene to FBX with VRChat-compatible settings"""
    print(f"Exporting to {OUTPUT_PATH}...")

    bpy.ops.export_scene.fbx(
        filepath=OUTPUT_PATH,

        # Object types
        object_types={'ARMATURE', 'MESH', 'EMPTY'},

        # Mesh options
        use_mesh_modifiers=True,
        use_mesh_modifiers_render=True,
        mesh_smooth_type='FACE',

        # Armature options
        use_armature_deform_only=True,
        add_leaf_bones=False,
        primary_bone_axis='Y',
        secondary_bone_axis='X',
        armature_nodetype='NULL',

        # Animation
        bake_anim=True,
        bake_anim_use_all_actions=True,
        bake_anim_use_nla_strips=False,
        bake_anim_step=1,
        bake_anim_simplify_factor=0,

        # Transform
        axis_forward='-Z',
        axis_up='Y',
        global_scale=1.0,
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_ALL',

        # Other
        use_space_transform=True,
        use_custom_props=False,
        path_mode='COPY',
        embed_textures=True,
    )

    print("FBX export complete!")

def main():
    """Main export pipeline"""
    import sys

    print("=" * 60)
    print("FBX EXPORT PIPELINE")
    print("=" * 60)
    print(f"Blender version: {bpy.app.version_string}")
    print(f"Python version: {sys.version}")
    print(f"Output path: {OUTPUT_PATH}")
    print("=" * 60 + "\n")

    try:
        # Load the final avatar
        blend_file = os.path.abspath("Avatar/ForgottenArchitect.blend")
        print(f"Loading avatar file: {blend_file}")

        if not os.path.exists(blend_file):
            print(f"✗ ERROR: {blend_file} not found!")
            print("Make sure generate_avatar.py and bake_textures.py have been run first.")
            return

        file_size = os.path.getsize(blend_file)
        print(f"File size: {file_size / 1024:.1f} KB")

        bpy.ops.wm.open_mainfile(filepath=blend_file)
        print("✓ Avatar file loaded\n")

        # Verify scene has required content
        mesh_count = len([obj for obj in bpy.data.objects if obj.type == 'MESH' and not obj.name.startswith('WGT-')])
        armature_count = len([obj for obj in bpy.data.objects if obj.type == 'ARMATURE'])

        print(f"Scene contents:")
        print(f"  Mesh objects: {mesh_count}")
        print(f"  Armatures: {armature_count}")

        if mesh_count == 0:
            print("✗ ERROR: No mesh objects found!")
            return

        if armature_count == 0:
            print("⚠ WARNING: No armature found - FBX may not rig properly!")

        print()

        # Prepare for export
        print("STEP 1: Preparing for export...")
        prepare_for_export()
        print("  ✓ Export preparation complete\n")

        # Export to FBX
        print("STEP 2: Exporting to FBX...")
        export_to_fbx()
        print("  ✓ FBX export complete\n")

        # Verify FBX was created
        if os.path.exists(OUTPUT_PATH):
            fbx_size = os.path.getsize(OUTPUT_PATH)
            print(f"✓ FBX file created: {OUTPUT_PATH}")
            print(f"✓ FBX file size: {fbx_size / 1024:.1f} KB")

            if fbx_size < 10000:
                print("⚠ WARNING: FBX file is very small - export may have failed!")
        else:
            print("✗ ERROR: FBX file was not created!")
            return

        print("\n" + "=" * 60)
        print("✓ FBX EXPORT COMPLETE!")
        print("=" * 60)
        print("Ready for Unity import!")

    except Exception as e:
        print("\n" + "=" * 60)
        print("✗ FATAL ERROR DURING FBX EXPORT")
        print("=" * 60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 60)
        raise

if __name__ == "__main__":
    main()
