#!/usr/bin/env python3
"""
Animation Creation Script for The Penitent Mechanism
Creates horror-themed animations:
- Idle (subtle swaying, mechanical breathing)
- Emote 1: Prayer Unfold (arms raise from prayer to T-pose, blade-fingers separate)
- Emote 2: Rise from Knees (legs telescope from kneeling to standing)
- Emote 3: Meditation Glitch (head rotates 360° on segmented neck, halo spins)
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
    Create unsettling idle animation for kneeling statue:
    - Slow mechanical breathing (chest expansion)
    - Subtle swaying (barely perceptible)
    - Finger micro-movements on fused blade-hands
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

    # Mechanical breathing - chest bone
    if 'spine.003' in rig.pose.bones or 'chest' in rig.pose.bones:
        chest_bone = rig.pose.bones.get('spine.003') or rig.pose.bones.get('chest')

        # Keyframe breathing cycle (slower, more mechanical)
        for frame in [1, 60, 120]:
            bpy.context.scene.frame_set(frame)
            scale_factor = 1.0 if frame == 60 else 1.015  # Subtler breathing
            chest_bone.scale = (scale_factor, scale_factor, scale_factor)
            chest_bone.keyframe_insert(data_path="scale", frame=frame)

    # Subtle swaying (kneeling statue barely moves)
    if 'spine' in rig.pose.bones:
        spine_bone = rig.pose.bones['spine']

        for frame in [1, 60, 120]:
            bpy.context.scene.frame_set(frame)
            sway_angle = 0.01 if frame == 60 else 0.0  # Tiny sway
            spine_bone.rotation_euler[0] = sway_angle  # X-axis sway
            spine_bone.keyframe_insert(data_path="rotation_euler", frame=frame)

    # Finger micro-movements (blade-hands twitch)
    finger_bones = [b for b in rig.pose.bones if 'finger' in b.name.lower()]
    for bone in finger_bones[:2]:  # Just a few fingers
        for frame in [1, 60, 120]:
            bpy.context.scene.frame_set(frame)
            twitch = 0.05 if frame == 60 else 0.0
            bone.rotation_euler[0] = twitch
            bone.keyframe_insert(data_path="rotation_euler", frame=frame)

    bpy.ops.object.mode_set(mode='OBJECT')

    # Export animation
    export_animation(action, "Idle")

def create_prayer_unfold_animation(rig):
    """
    Emote: Arms raise from prayer position to T-pose, blade-fingers separate slightly
    """
    print("Creating prayer unfold animation...")

    action = bpy.data.actions.new(name="PrayerUnfold")
    rig.animation_data.action = action

    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 60  # 2 seconds

    bpy.ops.object.mode_set(mode='POSE')

    # Both arms raise from prayer (hands at chest) to T-pose (arms out to sides)
    for side in ['L', 'R']:
        # Upper arm
        if f'upper_arm.{side}' in rig.pose.bones:
            arm_bone = rig.pose.bones[f'upper_arm.{side}']

            # Start in prayer position (arms at chest, rotated inward)
            bpy.context.scene.frame_set(1)
            if side == 'L':
                arm_bone.rotation_euler = (0, 0, 0.5)  # Arms inward
            else:
                arm_bone.rotation_euler = (0, 0, -0.5)
            arm_bone.keyframe_insert(data_path="rotation_euler", frame=1)

            # Mid-raise
            bpy.context.scene.frame_set(30)
            if side == 'L':
                arm_bone.rotation_euler = (0, 0, 0.785)  # 45 degrees out
            else:
                arm_bone.rotation_euler = (0, 0, -0.785)
            arm_bone.keyframe_insert(data_path="rotation_euler", frame=30)

            # T-pose (arms fully extended to sides)
            bpy.context.scene.frame_set(60)
            if side == 'L':
                arm_bone.rotation_euler = (0, 0, 1.57)  # 90 degrees (T-pose)
            else:
                arm_bone.rotation_euler = (0, 0, -1.57)
            arm_bone.keyframe_insert(data_path="rotation_euler", frame=60)

        # Forearm extends
        if f'forearm.{side}' in rig.pose.bones:
            forearm = rig.pose.bones[f'forearm.{side}']

            for frame, angle in [(1, -1.0), (30, -0.5), (60, 0.0)]:
                bpy.context.scene.frame_set(frame)
                forearm.rotation_euler = (0, angle, 0)
                forearm.keyframe_insert(data_path="rotation_euler", frame=frame)

    # Blade-fingers separate slightly (opening gesture)
    finger_bones = [b for b in rig.pose.bones if 'finger' in b.name.lower()]
    for bone in finger_bones:
        for frame, spread in [(1, 0.0), (60, 0.1)]:
            bpy.context.scene.frame_set(frame)
            bone.rotation_euler[2] = spread  # Slight spreading
            bone.keyframe_insert(data_path="rotation_euler", frame=frame)

    bpy.ops.object.mode_set(mode='OBJECT')
    export_animation(action, "PrayerUnfold")

def create_rise_from_knees_animation(rig):
    """
    Emote: Legs telescope from kneeling (1.8m) to standing (2.4m) height
    """
    print("Creating rise from knees animation...")

    action = bpy.data.actions.new(name="RiseFromKnees")
    rig.animation_data.action = action

    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 90  # 3 seconds

    bpy.ops.object.mode_set(mode='POSE')

    # Pelvis rises (main height change)
    if 'spine' in rig.pose.bones:
        pelvis = rig.pose.bones['spine']

        # Start kneeling
        bpy.context.scene.frame_set(1)
        pelvis.location = (0, 0, 0)
        pelvis.keyframe_insert(data_path="location", frame=1)

        # Rising
        bpy.context.scene.frame_set(45)
        pelvis.location = (0, 0, 0.3)  # Rising
        pelvis.keyframe_insert(data_path="location", frame=45)

        # Fully standing (60cm higher)
        bpy.context.scene.frame_set(90)
        pelvis.location = (0, 0, 0.6)
        pelvis.keyframe_insert(data_path="location", frame=90)

    # Thighs extend (legs telescope)
    for side in ['L', 'R']:
        if f'thigh.{side}' in rig.pose.bones:
            thigh = rig.pose.bones[f'thigh.{side}']

            # Start bent (kneeling)
            bpy.context.scene.frame_set(1)
            thigh.rotation_euler = (-1.57, 0, 0)  # 90 degrees bent
            thigh.scale = (1, 1, 1)
            thigh.keyframe_insert(data_path="rotation_euler", frame=1)
            thigh.keyframe_insert(data_path="scale", frame=1)

            # Extending
            bpy.context.scene.frame_set(45)
            thigh.rotation_euler = (-0.785, 0, 0)  # 45 degrees
            thigh.scale = (1, 1, 1.2)  # Telescoping
            thigh.keyframe_insert(data_path="rotation_euler", frame=45)
            thigh.keyframe_insert(data_path="scale", frame=45)

            # Fully extended (standing)
            bpy.context.scene.frame_set(90)
            thigh.rotation_euler = (0, 0, 0)  # Straight
            thigh.scale = (1, 1, 1.4)  # Fully telescoped
            thigh.keyframe_insert(data_path="rotation_euler", frame=90)
            thigh.keyframe_insert(data_path="scale", frame=90)

        # Shins also extend
        if f'shin.{side}' in rig.pose.bones:
            shin = rig.pose.bones[f'shin.{side}']

            for frame, angle, scale in [(1, -1.2, 1.0), (45, -0.6, 1.15), (90, 0.0, 1.3)]:
                bpy.context.scene.frame_set(frame)
                shin.rotation_euler = (angle, 0, 0)
                shin.scale = (1, 1, scale)
                shin.keyframe_insert(data_path="rotation_euler", frame=frame)
                shin.keyframe_insert(data_path="scale", frame=frame)

    bpy.ops.object.mode_set(mode='OBJECT')
    export_animation(action, "RiseFromKnees")

def create_meditation_glitch_animation(rig):
    """
    Emote: Head rotates 360° on segmented neck, halo spins rapidly
    """
    print("Creating meditation glitch animation...")

    action = bpy.data.actions.new(name="MeditationGlitch")
    rig.animation_data.action = action

    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 120  # 4 seconds

    bpy.ops.object.mode_set(mode='POSE')

    # Head rotates 360° on Z-axis (looking around)
    if 'head' in rig.pose.bones:
        head = rig.pose.bones['head']

        # Full 360° rotation
        bpy.context.scene.frame_set(1)
        head.rotation_euler = (0, 0, 0)
        head.keyframe_insert(data_path="rotation_euler", frame=1)

        bpy.context.scene.frame_set(30)
        head.rotation_euler = (0, 0, 1.57)  # 90°
        head.keyframe_insert(data_path="rotation_euler", frame=30)

        bpy.context.scene.frame_set(60)
        head.rotation_euler = (0, 0, 3.14)  # 180°
        head.keyframe_insert(data_path="rotation_euler", frame=60)

        bpy.context.scene.frame_set(90)
        head.rotation_euler = (0, 0, 4.71)  # 270°
        head.keyframe_insert(data_path="rotation_euler", frame=90)

        bpy.context.scene.frame_set(120)
        head.rotation_euler = (0, 0, 6.28)  # 360° (full rotation)
        head.keyframe_insert(data_path="rotation_euler", frame=120)

    # Neck segments crane unnaturally
    if 'neck' in rig.pose.bones:
        neck = rig.pose.bones['neck']

        # Neck bends and straightens during rotation
        for frame, angle in [(1, 0.0), (30, 0.2), (60, 0.0), (90, -0.2), (120, 0.0)]:
            bpy.context.scene.frame_set(frame)
            neck.rotation_euler = (angle, 0, 0)  # Forward/backward craning
            neck.keyframe_insert(data_path="rotation_euler", frame=frame)

    # Note: Halo spinning would need object-level animation (not bone)
    # For now, we'll simulate it with spine rotation
    if 'spine.004' in rig.pose.bones:  # Upper spine (halo attached)
        upper_spine = rig.pose.bones['spine.004']

        # Rapid spin effect
        for frame in range(1, 121, 10):
            bpy.context.scene.frame_set(frame)
            rotation = (frame / 120.0) * 12.56  # Multiple rotations
            upper_spine.rotation_euler = (0, 0, rotation)
            upper_spine.keyframe_insert(data_path="rotation_euler", frame=frame)

    bpy.ops.object.mode_set(mode='OBJECT')
    export_animation(action, "MeditationGlitch")

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
    print("ANIMATION CREATION PIPELINE - The Penitent Mechanism")
    print("=" * 60)
    print(f"Blender version: {bpy.app.version_string}")
    print(f"Python version: {sys.version}")
    print(f"Animation output directory: {ANIM_OUTPUT_DIR}")
    print("=" * 60 + "\n")

    try:
        # Load the rigged avatar
        blend_file = os.path.abspath("Avatar/PenitentMechanism.blend")
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

        # Create animations for The Penitent Mechanism
        print("STEP 1: Creating idle animation...")
        create_idle_animation(rig)
        print("  ✓ Idle animation created\n")

        print("STEP 2: Creating Prayer Unfold animation...")
        create_prayer_unfold_animation(rig)
        print("  ✓ Prayer Unfold animation created\n")

        print("STEP 3: Creating Rise from Knees animation...")
        create_rise_from_knees_animation(rig)
        print("  ✓ Rise from Knees animation created\n")

        print("STEP 4: Creating Meditation Glitch animation...")
        create_meditation_glitch_animation(rig)
        print("  ✓ Meditation Glitch animation created\n")

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
