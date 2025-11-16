# 🚀 Quick Start Guide

Get **The Forgotten Architect** avatar running in 5 minutes!

---

## Option 1: Download Pre-Built (Easiest) ⚡

### Step 1: Download
1. Go to [Actions tab](../../actions)
2. Click the latest green ✅ workflow run
3. Scroll down to **Artifacts**
4. Download `ForgottenArchitect-Avatar.zip`

### Step 2: Install Unity
1. Download [Unity Hub](https://unity.com/download)
2. Install **Unity 2022.3.22f1 LTS** via Unity Hub
3. Install VRChat Creator Companion: https://vcc.docs.vrchat.com/

### Step 3: Open Project
1. Extract the downloaded ZIP
2. Open Unity Hub
3. Click **Add** → select the `Project/` folder
4. Wait for Unity to import (5-10 min)

### Step 4: Install VRChat SDK
1. Open VRChat Creator Companion (VCC)
2. Add the project
3. Click **Manage Project**
4. Install **Avatars 3.0 SDK** (latest)

### Step 5: Upload to VRChat
1. In Unity: `VRChat SDK → Show Control Panel`
2. Sign in to your VRChat account
3. Select the `ForgottenArchitect` prefab in the scene
4. Click **Build & Publish**
5. Fill in avatar details:
   - Name: "The Forgotten Architect"
   - Description: "Biomechanical horror avatar"
   - Sharing: Public/Private (your choice)
6. Click **Upload**

### Step 6: Test in VRChat
1. Launch VRChat
2. Go to Avatar menu
3. Select "The Forgotten Architect"
4. Try the emotes! (Expressions menu)

---

## Option 2: Build from Source 🛠️

### Prerequisites
- Blender 3.6+ ([Download](https://www.blender.org/download/))
- Python 3.8+ ([Download](https://www.python.org/downloads/))
- Unity 2022.3.22f1 ([Download](https://unity.com/releases/editor/archive))

### Step 1: Clone Repository
```bash
git clone https://github.com/jakubkrzysztofsikora/Vrchat-avatar.git
cd Vrchat-avatar
```

### Step 2: Run Blender Scripts
```bash
# 1. Generate 3D model
blender --background --python scripts/blender/generate_avatar.py

# 2. Bake textures
blender --background --python scripts/blender/bake_textures.py

# 3. Create animations
blender --background --python scripts/blender/create_animations.py

# 4. Export to FBX
blender --background --python scripts/blender/export_fbx.py

# 5. Render screenshots (optional)
blender --background --python scripts/blender/render_screenshots.py
```

**Expected time**: ~30-60 minutes depending on your CPU

### Step 3: Open in Unity
1. Open Unity 2022.3.22f1
2. Open the `Project/` folder
3. Wait for import to complete
4. Install VRChat SDK via VCC

### Step 4: Run Unity Setup
1. In Unity: `Window → VRChat → Setup Forgotten Architect Avatar`
2. Wait for setup to complete
3. Check Console for any errors

### Step 5: Upload
Same as Option 1, Step 5

---

## Option 3: GitHub Actions (Fully Automated) 🤖

### Trigger the Build

**Method A: Push to Main**
```bash
git add .
git commit -m "Trigger avatar build"
git push origin main
```

**Method B: Manual Dispatch**
1. Go to [Actions tab](../../actions)
2. Select **Build VRChat Avatar & Generate Screenshots**
3. Click **Run workflow** → **Run workflow**

### Wait for Build
- Check the Actions tab for progress
- Build takes ~30-90 minutes
- Download artifact when complete

### Use the Avatar
Follow Option 1 steps 2-6

---

## 🎮 Testing Your Avatar

### In Unity (Before Upload)

1. **Scene View**: Check model appearance
2. **Animator**: Open `FX_Controller.controller`, test animations
3. **Avatar Descriptor**: Verify "Good" performance rank
4. **Viewpoint**: Ensure eye position is correct (should be ~1.65m high)

### In VRChat

1. **Movement**: Walk around, ensure no clipping
2. **Emotes**: Test all 3 horror emotes
   - Mechanical Unfold (toggle)
   - System Reboot (one-shot)
   - The Stare (toggle)
3. **Mirrors**: Check appearance from all angles
4. **Performance**: Monitor FPS (should be 60+ on decent PC)

---

## ❓ Troubleshooting

### "FBX not found" in Unity
- Re-run `export_fbx.py` script
- Check `Avatar/` folder for `.fbx` file
- Manually copy `ForgottenArchitect.fbx` to `Project/Assets/ForgottenArchitect/`

### "VRChat SDK not found"
- Install via VRChat Creator Companion
- Manually add to Unity Package Manager:
  - Add scoped registry: `https://packages.vrchat.com`
  - Install `com.vrchat.avatars`

### "Avatar Descriptor missing"
- Run Unity setup: `Window → VRChat → Setup Forgotten Architect Avatar`
- Or manually add `VRCAvatarDescriptor` component to avatar root

### "Performance rank is Poor"
- Check polygon count (target: <40k tris)
- Reduce texture resolution in Blender script
- Disable unnecessary mesh parts

### "Animations not playing"
- Verify FX Controller is assigned in Avatar Descriptor
- Check Expression Parameters are linked
- Ensure animations were exported from Blender

---

## 🎨 Customization Tips

### Change Avatar Height
Edit `scripts/blender/generate_avatar.py`:
```python
AVATAR_HEIGHT = 2.1  # Change this value (in meters)
```

### Modify Colors
Edit material functions in `generate_avatar.py`:
```python
bsdf.inputs['Base Color'].default_value = (R, G, B, 1.0)
```

### Add New Emotes
1. Create animation function in `create_animations.py`
2. Add parameter in `SetupAvatar.cs`
3. Add control to expressions menu

---

## 📚 Next Steps

- **Read full README**: [README.md](../README.md)
- **Development log**: [CLAUDE.md](../CLAUDE.md)
- **Report issues**: [GitHub Issues](../../issues)
- **Join discussions**: [GitHub Discussions](../../discussions)

---

## 🆘 Getting Help

**Common Issues**: Check [Troubleshooting](#-troubleshooting) above

**Still Stuck?**
1. Check [GitHub Issues](../../issues) for similar problems
2. Create a new issue with:
   - Error message
   - Build logs
   - Unity version
   - VRChat SDK version

**Discord Communities**:
- VRChat Official Discord
- Unity Discord

---

<div align="center">

**🎭 Happy Haunting! 🎭**

*May your circuits corrupt gracefully.*

</div>
