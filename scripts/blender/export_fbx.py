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
                    print(f"Applied modifier {modifier.name} on {obj.name}")
                except Exception as e:
                    print(f"Could not apply modifier {modifier.name} on {obj.name}: {e}")

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
    print("=" * 60)
    print("FBX EXPORT PIPELINE")
    print("=" * 60)

    # Load the final avatar
    blend_file = os.path.abspath("Avatar/ForgottenArchitect.blend")
    if os.path.exists(blend_file):
        bpy.ops.wm.open_mainfile(filepath=blend_file)
    else:
        print(f"ERROR: {blend_file} not found!")
        return

    prepare_for_export()
    export_to_fbx()

    print(f"Avatar exported to: {OUTPUT_PATH}")
    print("Ready for Unity import!")

if __name__ == "__main__":
    main()
