#!/usr/bin/env python3
"""
Screenshot Rendering Script for The Forgotten Architect
Renders 5 high-quality views:
- Front view
- Back view
- Close-up face
- Pose 1 (Mechanical Unfold)
- Pose 2 (The Stare)
"""

import bpy
import os
from mathutils import Vector

OUTPUT_DIR = os.path.abspath("docs/screenshots")
RESOLUTION_X = 1920
RESOLUTION_Y = 1080

def setup_render_settings():
    """Configure render settings for high-quality screenshots"""
    print("Configuring render settings...")

    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 256  # High quality
    scene.render.resolution_x = RESOLUTION_X
    scene.render.resolution_y = RESOLUTION_Y
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False  # Dark background for horror aesthetic

    # Color management
    scene.view_settings.view_transform = 'Filmic'
    scene.view_settings.look = 'Medium High Contrast'

def setup_lighting():
    """Create dramatic horror lighting"""
    print("Setting up lighting...")

    # Clear existing lights
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT':
            obj.select_set(True)
    bpy.ops.object.delete()

    # Key light (cold blue - left side)
    bpy.ops.object.light_add(type='AREA', location=(3, -2, 2))
    key_light = bpy.context.active_object
    key_light.data.energy = 100
    key_light.data.color = (0.7, 0.8, 1.0)  # Cold blue
    key_light.data.size = 2

    # Rim light (warm amber - right side, from behind)
    bpy.ops.object.light_add(type='AREA', location=(-2, 3, 2.5))
    rim_light = bpy.context.active_object
    rim_light.data.energy = 80
    rim_light.data.color = (1.0, 0.6, 0.2)  # Amber (Dwemer glow)
    rim_light.data.size = 1.5

    # Fill light (very dim, from front)
    bpy.ops.object.light_add(type='AREA', location=(0, -4, 1.5))
    fill_light = bpy.context.active_object
    fill_light.data.energy = 20
    fill_light.data.color = (0.9, 0.9, 0.9)
    fill_light.data.size = 3

    # Top light (dim, for form definition)
    bpy.ops.object.light_add(type='POINT', location=(0, 0, 4))
    top_light = bpy.context.active_object
    top_light.data.energy = 50
    top_light.data.color = (0.8, 0.8, 1.0)

def setup_camera():
    """Create camera for rendering"""
    print("Setting up camera...")

    # Clear existing cameras
    for obj in bpy.data.objects:
        if obj.type == 'CAMERA':
            bpy.data.objects.remove(obj, do_unlink=True)

    # Create new camera
    bpy.ops.object.camera_add(location=(0, -4, 1.5))
    camera = bpy.context.active_object
    camera.name = "RenderCamera"

    # Set as active camera
    bpy.context.scene.camera = camera

    # Camera settings
    camera.data.lens = 50  # Portrait lens
    camera.data.dof.use_dof = True
    camera.data.dof.aperture_fstop = 2.8  # Shallow depth of field

    return camera

def setup_environment():
    """Create dark, ominous background"""
    print("Setting up environment...")

    # World settings
    world = bpy.data.worlds.get('World')
    if not world:
        world = bpy.data.worlds.new('World')
        bpy.context.scene.world = world

    world.use_nodes = True
    nodes = world.node_tree.nodes
    nodes.clear()

    # Background shader
    bg = nodes.new(type='ShaderNodeBackground')
    bg.inputs['Color'].default_value = (0.02, 0.02, 0.03, 1.0)  # Very dark blue
    bg.inputs['Strength'].default_value = 0.5

    output = nodes.new(type='ShaderNodeOutputWorld')
    world.node_tree.links.new(bg.outputs['Background'], output.inputs['Surface'])

def find_avatar_rig():
    """Find the avatar armature"""
    print("Searching for avatar rig...")
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE' and 'Forgotten' in obj.name:
            print(f"  Found rig: {obj.name}")
            return obj
    # Fallback: return first armature
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE':
            print(f"  Found armature (fallback): {obj.name}")
            return obj
    print("  ERROR: No armature found in scene!")
    return None

def validate_scene():
    """Validate scene has required objects and geometry"""
    print("Validating scene before rendering...")

    issues = []

    # Check for armature
    rig = find_avatar_rig()
    if not rig:
        issues.append("No armature found")

    # Check for mesh objects
    mesh_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH' and not obj.name.startswith('WGT-')]
    if len(mesh_objects) == 0:
        issues.append("No mesh objects found")
    else:
        print(f"  Found {len(mesh_objects)} mesh objects:")
        total_verts = 0
        for obj in mesh_objects:
            vert_count = len(obj.data.vertices)
            total_verts += vert_count
            print(f"    - {obj.name}: {vert_count} vertices")

        if total_verts < 100:
            issues.append(f"Very low vertex count: {total_verts} (expected >100)")

    # Check scene bounds (should be humanoid-sized)
    if mesh_objects:
        # Calculate combined bounding box
        all_coords = []
        for obj in mesh_objects:
            for v in obj.data.vertices:
                all_coords.append(obj.matrix_world @ v.co)

        if all_coords:
            min_z = min(v.z for v in all_coords)
            max_z = max(v.z for v in all_coords)
            height = max_z - min_z

            print(f"  Scene height: {height:.2f}m (min_z: {min_z:.2f}, max_z: {max_z:.2f})")

            if height < 1.0:
                issues.append(f"Scene height too small: {height:.2f}m (expected ~2m)")

            # Check if geometry is near origin (not floating far away)
            if min_z > 5.0 or min_z < -5.0:
                issues.append(f"Geometry is far from origin (min_z: {min_z:.2f}m)")

    if issues:
        print("  ⚠ VALIDATION WARNINGS:")
        for issue in issues:
            print(f"    - {issue}")
        print("  Rendering will continue but results may be incorrect")
        return False
    else:
        print("  ✓ Scene validation passed")
        return True

def get_rig_target(rig):
    """Return a point for the camera to look at (chest/head area, not feet)."""
    if rig:
        # Target the chest/head area, not the armature origin (which is at feet)
        # Avatar is ~2.1m tall, so chest is around 1.4-1.6m
        rig_origin = rig.matrix_world.translation
        chest_height = Vector((rig_origin.x, rig_origin.y, rig_origin.z + 1.5))
        return chest_height
    return Vector((0.0, 0.0, 1.5))


def point_camera_at(camera, target_point):
    """Rotate the camera so it looks at the provided target point."""
    direction = target_point - camera.location
    if direction.length < 1e-6:
        return
    rotation = direction.to_track_quat('-Z', 'Y').to_euler()
    camera.rotation_euler = rotation


def position_camera_for_view(camera, view_type, rig):
    """Position camera for specific view"""
    print(f"Positioning camera for {view_type}...")

    target_point = get_rig_target(rig)
    print(f"  Camera target: {target_point}")

    # Full body shots - camera positioned to show entire avatar
    if view_type == 'front':
        camera.location = (0, -5.5, 1.2)  # Further back to capture full body
        camera.data.lens = 35  # Wider lens
        print(f"  Front view: camera at {camera.location}, lens {camera.data.lens}mm")

    elif view_type == 'back':
        camera.location = (0, 5.5, 1.2)
        camera.data.lens = 35
        print(f"  Back view: camera at {camera.location}, lens {camera.data.lens}mm")

    elif view_type == 'face':
        # Close-up of face/mechanical eye
        face_target = Vector((target_point.x, target_point.y, target_point.z + 0.3))  # Aim at head
        camera.location = (0.3, -1.2, 1.95)  # Offset to right side (mechanical side)
        camera.data.lens = 85  # Portrait lens
        point_camera_at(camera, face_target)
        print(f"  Face closeup: camera at {camera.location}, targeting {face_target}")
        return  # Skip the main point_camera_at call below

    elif view_type == 'pose1':
        # Mechanical unfold - 3/4 side view to show both front and side
        camera.location = (3.5, -2.5, 1.2)
        camera.data.lens = 40
        print(f"  Pose 1 (mech unfold): camera at {camera.location}, lens {camera.data.lens}mm")

    elif view_type == 'pose2':
        # The stare - front 3/4 view
        camera.location = (1.8, -4.0, 1.4)
        camera.data.lens = 45
        print(f"  Pose 2 (the stare): camera at {camera.location}, lens {camera.data.lens}mm")

    point_camera_at(camera, target_point)

def apply_pose(rig, pose_name):
    """Apply animation pose for screenshot"""
    print(f"Applying pose: {pose_name}")

    if not rig or rig.animation_data is None:
        return

    # Find action
    action = bpy.data.actions.get(pose_name)
    if not action:
        print(f"Warning: Action {pose_name} not found")
        return

    rig.animation_data.action = action

    # Set frame to mid-point of animation (most dramatic pose)
    if pose_name == "MechanicalUnfold":
        bpy.context.scene.frame_set(30)
    elif pose_name == "TheStare":
        bpy.context.scene.frame_set(60)

def render_view(camera, view_type, rig=None, pose=None):
    """Render a specific view"""
    print(f"Rendering {view_type}...")

    # Apply pose if specified
    if pose and rig:
        apply_pose(rig, pose)

    # Position camera
    position_camera_for_view(camera, view_type, rig)

    # Render
    output_path = os.path.join(OUTPUT_DIR, f"{view_type}.png")
    bpy.context.scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)

    print(f"Saved: {output_path}")

def main():
    """Main rendering pipeline"""
    print("=" * 60)
    print("SCREENSHOT RENDERING PIPELINE")
    print("=" * 60)

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load the avatar
    blend_file = os.path.abspath("Avatar/ForgottenArchitect.blend")
    if os.path.exists(blend_file):
        bpy.ops.wm.open_mainfile(filepath=blend_file)
    else:
        print(f"ERROR: {blend_file} not found!")
        return

    # Validate scene first
    validation_passed = validate_scene()
    if not validation_passed:
        print("⚠ Scene validation failed - screenshots may not render correctly!")

    # Setup scene
    setup_render_settings()
    setup_environment()
    setup_lighting()
    camera = setup_camera()

    # Find rig
    rig = find_avatar_rig()
    if not rig:
        print("ERROR: No rig found - cannot position camera!")
        print("Attempting to render anyway with default camera position...")

    # Render views
    render_view(camera, 'front', rig)
    render_view(camera, 'back', rig)
    render_view(camera, 'face', rig)
    render_view(camera, 'pose1', rig, pose='MechanicalUnfold')
    render_view(camera, 'pose2', rig, pose='TheStare')

    print("=" * 60)
    print("Screenshot rendering complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
