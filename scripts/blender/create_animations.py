#!/usr/bin/env python3
"""
Animation Creation Script for The Forgotten Architect
Creates horror-themed animations:
- Idle (breathing with mechanical sounds)
- Emote 1: Mechanical Unfold (parts telescope outward)
- Emote 2: System Reboot (glitchy reset)
- Emote 3: The Stare (uncanny face focus)
"""

import bpy
import math
import os

ANIM_OUTPUT_DIR = os.path.abspath("Avatar/Animations")

def clear_animation(obj):
    """Clear existing animation data"""
    if obj.animation_data:
        obj.animation_data_clear()

def create_idle_animation(rig):
    """
    Create unsettling idle animation:
    - Slow breathing (chest expansion)
    - Mechanical parts subtle grinding
    - Head micro-twitches
    - Fingers slow curl/uncurl
    """
    print("Creating idle animation...")

    # Create action
    action = bpy.data.actions.new(name="Idle")
    rig.animation_data_create()
    rig.animation_data.action = action

    # Set frame range
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 120  # 4 seconds at 30fps

    # Enter pose mode
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode='POSE')

    # Breathing - chest bone
    if 'spine.003' in rig.pose.bones or 'chest' in rig.pose.bones:
        chest_bone = rig.pose.bones.get('spine.003') or rig.pose.bones.get('chest')

        # Keyframe breathing cycle
        for frame in [1, 60, 120]:
            bpy.context.scene.frame_set(frame)
            scale_factor = 1.0 if frame == 60 else 1.02
            chest_bone.scale = (scale_factor, scale_factor, scale_factor)
            chest_bone.keyframe_insert(data_path="scale", frame=frame)

    # Head micro-twitches
    if 'head' in rig.pose.bones:
        head_bone = rig.pose.bones['head']

        twitch_frames = [30, 31, 75, 76]
        for frame in twitch_frames:
            bpy.context.scene.frame_set(frame)
            angle = 0.05 if frame % 2 == 0 else -0.03
            head_bone.rotation_euler[2] = angle  # Z-axis rotation
            head_bone.keyframe_insert(data_path="rotation_euler", frame=frame)

        # Return to neutral
        for frame in [1, 40, 90, 120]:
            bpy.context.scene.frame_set(frame)
            head_bone.rotation_euler = (0, 0, 0)
            head_bone.keyframe_insert(data_path="rotation_euler", frame=frame)

    # Finger curl (right hand - mechanical side)
    finger_bones = [b for b in rig.pose.bones if 'finger' in b.name.lower() and 'r' in b.name.lower()]
    for bone in finger_bones[:3]:  # Just a few fingers
        for frame in [1, 60, 120]:
            bpy.context.scene.frame_set(frame)
            curl = 0.2 if frame == 60 else 0.0
            bone.rotation_euler[0] = curl
            bone.keyframe_insert(data_path="rotation_euler", frame=frame)

    bpy.ops.object.mode_set(mode='OBJECT')

    # Export animation
    export_animation(action, "Idle")

def create_mechanical_unfold_animation(rig):
    """
    Emote: Mechanical parts telescope outward revealing inner mechanisms
    """
    print("Creating mechanical unfold animation...")

    action = bpy.data.actions.new(name="MechanicalUnfold")
    rig.animation_data.action = action

    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 60

    bpy.ops.object.mode_set(mode='POSE')

    # Right arm extends unnaturally
    if 'upper_arm.R' in rig.pose.bones:
        arm_bone = rig.pose.bones['upper_arm.R']

        # Start pose
        bpy.context.scene.frame_set(1)
        arm_bone.rotation_euler = (0, 0, 0)
        arm_bone.scale = (1, 1, 1)
        arm_bone.keyframe_insert(data_path="rotation_euler", frame=1)
        arm_bone.keyframe_insert(data_path="scale", frame=1)

        # Extended pose
        bpy.context.scene.frame_set(30)
        arm_bone.rotation_euler = (0, 0, -1.5)  # Extend outward
        arm_bone.scale = (1, 1.3, 1)  # Elongate
        arm_bone.keyframe_insert(data_path="rotation_euler", frame=30)
        arm_bone.keyframe_insert(data_path="scale", frame=30)

        # Return
        bpy.context.scene.frame_set(60)
        arm_bone.rotation_euler = (0, 0, 0)
        arm_bone.scale = (1, 1, 1)
        arm_bone.keyframe_insert(data_path="rotation_euler", frame=60)
        arm_bone.keyframe_insert(data_path="scale", frame=60)

    # Chest plates separate
    if 'spine.003' in rig.pose.bones:
        chest = rig.pose.bones['spine.003']

        for frame, scale in [(1, 1.0), (30, 1.15), (60, 1.0)]:
            bpy.context.scene.frame_set(frame)
            chest.scale = (scale, scale, 1.0)
            chest.keyframe_insert(data_path="scale", frame=frame)

    bpy.ops.object.mode_set(mode='OBJECT')
    export_animation(action, "MechanicalUnfold")

def create_system_reboot_animation(rig):
    """
    Emote: Glitchy system reboot - jerky movements, reset to T-pose briefly
    """
    print("Creating system reboot animation...")

    action = bpy.data.actions.new(name="SystemReboot")
    rig.animation_data.action = action

    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 90

    bpy.ops.object.mode_set(mode='POSE')

    # Get all pose bones
    all_bones = list(rig.pose.bones)

    # Glitch phase (frames 1-30)
    for frame in range(1, 30, 3):
        bpy.context.scene.frame_set(frame)
        for bone in all_bones[:10]:  # Just affect some bones
            bone.rotation_euler = (
                (hash(bone.name + str(frame)) % 100) / 1000.0,
                (hash(bone.name + str(frame + 1)) % 100) / 1000.0,
                (hash(bone.name + str(frame + 2)) % 100) / 1000.0
            )
            bone.keyframe_insert(data_path="rotation_euler", frame=frame)

    # T-pose reset (frame 45)
    bpy.context.scene.frame_set(45)
    for bone in all_bones:
        bone.rotation_euler = (0, 0, 0)
        bone.scale = (1, 1, 1)
        bone.keyframe_insert(data_path="rotation_euler", frame=45)
        bone.keyframe_insert(data_path="scale", frame=45)

    # Return to rest (frame 90)
    bpy.context.scene.frame_set(90)
    for bone in all_bones:
        bone.rotation_euler = (0, 0, 0)
        bone.keyframe_insert(data_path="rotation_euler", frame=90)

    bpy.ops.object.mode_set(mode='OBJECT')
    export_animation(action, "SystemReboot")

def create_the_stare_animation(rig):
    """
    Emote: Head slowly turns to camera, mechanical eye lenses focus
    """
    print("Creating 'The Stare' animation...")

    action = bpy.data.actions.new(name="TheStare")
    rig.animation_data.action = action

    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 120

    bpy.ops.object.mode_set(mode='POSE')

    # Head turn
    if 'head' in rig.pose.bones:
        head = rig.pose.bones['head']

        # Start neutral
        bpy.context.scene.frame_set(1)
        head.rotation_euler = (0, 0, 0)
        head.keyframe_insert(data_path="rotation_euler", frame=1)

        # Slow turn toward camera
        bpy.context.scene.frame_set(60)
        head.rotation_euler = (0.1, 0, 0)  # Slight tilt forward
        head.keyframe_insert(data_path="rotation_euler", frame=60)

        # Hold the stare
        bpy.context.scene.frame_set(90)
        head.rotation_euler = (0.1, 0, 0)
        head.keyframe_insert(data_path="rotation_euler", frame=90)

        # Return
        bpy.context.scene.frame_set(120)
        head.rotation_euler = (0, 0, 0)
        head.keyframe_insert(data_path="rotation_euler", frame=120)

    # Neck elongates slightly (horror effect)
    if 'neck' in rig.pose.bones:
        neck = rig.pose.bones['neck']

        for frame, scale in [(1, 1.0), (60, 1.15), (90, 1.15), (120, 1.0)]:
            bpy.context.scene.frame_set(frame)
            neck.scale = (1, 1, scale)
            neck.keyframe_insert(data_path="scale", frame=frame)

    bpy.ops.object.mode_set(mode='OBJECT')
    export_animation(action, "TheStare")

def export_animation(action, name):
    """Export animation as FBX"""
    os.makedirs(ANIM_OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(ANIM_OUTPUT_DIR, f"{name}.fbx")

    # FBX export with animation
    bpy.ops.export_scene.fbx(
        filepath=output_path,
        use_selection=False,
        bake_anim=True,
        bake_anim_use_all_actions=False,
        bake_anim_use_nla_strips=False,
        add_leaf_bones=False
    )

    print(f"Exported: {output_path}")

def main():
    """Main animation creation pipeline"""
    import sys

    print("=" * 60)
    print("ANIMATION CREATION PIPELINE")
    print("=" * 60)
    print(f"Blender version: {bpy.app.version_string}")
    print(f"Python version: {sys.version}")
    print(f"Animation output directory: {ANIM_OUTPUT_DIR}")
    print("=" * 60 + "\n")

    try:
        # Load the rigged avatar
        blend_file = os.path.abspath("Avatar/ForgottenArchitect.blend")
        print(f"Loading avatar file: {blend_file}")

        if not os.path.exists(blend_file):
            print(f"✗ ERROR: {blend_file} not found!")
            print("Make sure generate_avatar.py has been run first.")
            return

        file_size = os.path.getsize(blend_file)
        print(f"File size: {file_size / 1024:.1f} KB")

        bpy.ops.wm.open_mainfile(filepath=blend_file)
        print("✓ Avatar file loaded\n")

        # Find the rig
        print("Searching for armature...")
        rig = None
        armatures = [obj for obj in bpy.data.objects if obj.type == 'ARMATURE']

        if len(armatures) == 0:
            print("✗ ERROR: No armature found!")
            print("Cannot create animations without a rig.")
            return
        elif len(armatures) > 1:
            print(f"⚠ WARNING: Found {len(armatures)} armatures, using first one")
            for arm in armatures:
                print(f"  - {arm.name}")

        rig = armatures[0]
        print(f"✓ Using rig: {rig.name}")
        print(f"  Bones: {len(rig.data.bones)}")
        print(f"  Sample bones: {[b.name for b in list(rig.data.bones)[:5]]}\n")

        # Create animations
        print("STEP 1: Creating idle animation...")
        create_idle_animation(rig)
        print("  ✓ Idle animation created\n")

        print("STEP 2: Creating mechanical unfold animation...")
        create_mechanical_unfold_animation(rig)
        print("  ✓ Mechanical unfold animation created\n")

        print("STEP 3: Creating system reboot animation...")
        create_system_reboot_animation(rig)
        print("  ✓ System reboot animation created\n")

        print("STEP 4: Creating 'The Stare' animation...")
        create_the_stare_animation(rig)
        print("  ✓ 'The Stare' animation created\n")

        # List created actions
        actions = [action for action in bpy.data.actions]
        print(f"Created {len(actions)} actions:")
        for action in actions:
            frame_range = action.frame_range
            print(f"  - {action.name} (frames {frame_range[0]:.0f}-{frame_range[1]:.0f})")

        # Save
        print("\nSaving blend file with animations...")
        bpy.ops.wm.save_as_mainfile(filepath=blend_file)
        print("✓ File saved successfully!")

        # Verify animation files
        if os.path.exists(ANIM_OUTPUT_DIR):
            anim_files = [f for f in os.listdir(ANIM_OUTPUT_DIR) if f.endswith('.fbx')]
            print(f"\nExported {len(anim_files)} animation FBX files:")
            for anim_file in anim_files:
                anim_path = os.path.join(ANIM_OUTPUT_DIR, anim_file)
                anim_size = os.path.getsize(anim_path) / 1024
                print(f"  - {anim_file} ({anim_size:.1f} KB)")

        print("\n" + "=" * 60)
        print("✓ ANIMATION CREATION COMPLETE!")
        print("=" * 60)

    except Exception as e:
        print("\n" + "=" * 60)
        print("✗ FATAL ERROR DURING ANIMATION CREATION")
        print("=" * 60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 60)
        raise

if __name__ == "__main__":
    main()
