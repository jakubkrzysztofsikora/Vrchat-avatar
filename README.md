# 🎭 The Penitent Mechanism

<div align="center">

**A Fully Automated VRChat Horror Avatar**

*Buddhist Shrine Guardian Possessed by Dwemer Machinery*

[![Build VRChat Avatar](https://github.com/jakubkrzysztofsikora/Vrchat-avatar/actions/workflows/build.yml/badge.svg)](https://github.com/jakubkrzysztofsikora/Vrchat-avatar/actions/workflows/build.yml)

</div>

---

## 🌀 Concept

**The Penitent Mechanism** is an ancient Buddhist/Shinto shrine guardian statue possessed and corrupted by Dwemer machinery. This VRChat avatar embodies:

- **Elder Scrolls Horror**: Dwemer machinery animating sacred statuary, oxidized bronze construction, ancient mechanisms corrupting holy relics
- **Asian Horror Minimalism**: Shrine guardian aesthetic, kneeling penitent pose, featureless bronze mask, uncanny stillness punctuated by mechanical movement
- **Lovecraftian Wrongness**: Body segmentation defying anatomy, telescoping limbs, impossible prayer pose with fused blade-hands

### Horror Design Elements

- 🙏 **Eternal Penitent**: Locked in kneeling prayer pose (1.8m kneeling, 2.4m if standing)
- 🎭 **Bronze Mask Face**: Smooth featureless mask with almond eye cutouts - NO nose, NO mouth, NO expression
- 🗡️ **Fused Blade-Hands**: Fingers merged into single sharp points - cannot grasp, only pray and pierce
- 🦴 **Segmented Neck**: Multiple bronze rings allowing unnatural craning and rotation
- 🦿 **Telescoping Legs**: Can extend from kneeling to standing in disturbing mechanical sequence
- ☸️ **Mechanical Halo**: Rotating bronze rings behind head with Dwemer inscriptions and amber light
- 🎨 **Aged Bronze Aesthetic**: Dark oxidized bronze with green verdigris corruption, ivory joints, saffron prayer cloth

---

## 🎬 Avatar Preview (Auto-Updated)

<div align="center">

<!-- AUTO-GENERATED-SCREENSHOTS -->
<!-- Last updated: 2025-11-17 07:35:25 UTC -->

| | |
|:---:|:---:|
| **Front View**<br/><img src="docs/screenshots/front.png" alt="Front View" width="400"/> | **Back View**<br/><img src="docs/screenshots/back.png" alt="Back View" width="400"/> |
| **Face Detail (Mechanical Eye)**<br/><img src="docs/screenshots/face.png" alt="Face Detail (Mechanical Eye)" width="400"/> | **Emote: Mechanical Unfold**<br/><img src="docs/screenshots/pose1.png" alt="Emote: Mechanical Unfold" width="400"/> |
| **Emote: The Stare**<br/><img src="docs/screenshots/pose2.png" alt="Emote: The Stare" width="400"/> |  |

<!-- END-AUTO-GENERATED-SCREENSHOTS -->

</div>

---

## ⚡ Features

### 🤖 **100% Automated Build Pipeline**

This repository uses GitHub Actions to automatically:

1. ✅ **Procedurally generate** the entire 3D avatar model using Blender Python scripts
2. ✅ **Automatically rig** the model with Rigify humanoid armature
3. ✅ **Bake PBR textures** (Optimized: only bakes procedural materials, skips solid colors - 92% time reduction)
4. ✅ **Create horror animations** (Idle + 3 emotes)
5. ✅ **Export to FBX** with Unity-compatible settings
6. ✅ **Set up Unity VRChat project** with Avatar Descriptor, FX Animator, and Expressions Menu
7. ✅ **Render high-quality screenshots** (5 views)
8. ✅ **Update this README** with generated screenshots
9. ✅ **Commit everything back** to the repository

### 🎮 **VRChat Features**

- **SDK**: VRChat SDK3 (Avatars)
- **Rig**: Humanoid (full-body tracking compatible)
- **Performance Rank**: Good (target ~25-40k polygons)
- **Platform**: PC only (Quest not supported - uses advanced shaders)
- **Emotes**:
  - 🙏 **Prayer Unfold**: Arms raise from prayer to T-pose, fingers separate from blade-fused state
  - 🦿 **Rise from Knees**: Legs telescope from 1.8m kneeling to 2.4m standing height
  - 📿 **Meditation Glitch**: Head rotates 360° on segmented neck, halo rings spin rapidly with amber flare

### 🎨 **Materials & Shaders**

- **PBR Materials**: Physically-based rendering for aged bronze and sacred materials
- **Procedural Textures**: All textures generated algorithmically (no external assets)
- **MAT_Bronze**: Aged oxidized bronze with procedural noise-based green verdigris (the ONLY material requiring texture baking)
- **MAT_Ivory**: Smooth pale stone/ceramic for body segments (solid color, no baking needed)
- **MAT_Saffron_Bronze**: Warm brass for prayer cloth and accents (solid color, no baking needed)
- **MAT_Amber_Glow**: Glowing emission for halo lights and eye glow (simple emission, no baking needed)

---

## 📦 Installation & Usage

### Option 1: Download Pre-Built Avatar (Easiest)

1. Go to [Actions](https://github.com/jakubkrzysztofsikora/Vrchat-avatar/actions) tab
2. Click on the latest successful build
3. Download the `ForgottenArchitect-Avatar` artifact
4. Extract the archive
5. Open `Project/` in Unity 2022.3.22f1
6. Install VRChat SDK3 via [VRChat Creator Companion](https://vcc.docs.vrchat.com/)
7. Open the `ForgottenArchitect.prefab` in the Project window
8. Upload to VRChat!

### Option 2: Build Locally

#### Prerequisites
- **Blender 3.6+** with Rigify addon enabled
- **Unity 2022.3.22f1 LTS**
- **VRChat SDK3** (Avatars)
- **Python 3.8+**

#### Build Steps

```bash
# Clone repository
git clone https://github.com/jakubkrzysztofsikora/Vrchat-avatar.git
cd Vrchat-avatar

# Run Blender scripts (in order)
blender --background --python scripts/blender/generate_avatar.py
blender --background --python scripts/blender/bake_textures_optimized.py
blender --background --python scripts/blender/create_animations.py
blender --background --python scripts/blender/export_fbx.py
blender --background --python scripts/blender/render_screenshots.py

# Open Unity project
# Open Project/ in Unity 2022.3.22f1

# Run setup (in Unity)
# Window > VRChat > Setup Forgotten Architect Avatar

# Upload avatar to VRChat
# VRChat SDK > Show Control Panel > Build & Publish
```

### Option 3: Trigger GitHub Action

Just push to the `main` branch or manually trigger the workflow:

1. Go to **Actions** tab
2. Select **Build VRChat Avatar & Generate Screenshots**
3. Click **Run workflow**
4. Wait ~30-60 minutes for the build
5. Download the artifact and use in Unity!

---

## 🏗️ Architecture

### Repository Structure

```
Vrchat-avatar/
├── .github/
│   └── workflows/
│       └── build.yml              # Main CI/CD pipeline
├── scripts/
│   ├── blender/
│   │   ├── generate_avatar.py            # Procedural model generation (The Penitent Mechanism)
│   │   ├── bake_textures.py              # Original PBR texture baking (legacy)
│   │   ├── bake_textures_optimized.py    # Optimized baking (92% faster - ACTIVE)
│   │   ├── create_animations.py          # Horror animation creation
│   │   ├── export_fbx.py                 # Unity-compatible FBX export
│   │   └── render_screenshots.py         # Screenshot rendering
│   ├── unity/
│   │   └── SetupAvatar.cs         # VRChat avatar setup automation
│   └── update_readme.py           # README screenshot injection
├── Avatar/
│   ├── ForgottenArchitect.blend   # Source Blender file (generated)
│   ├── ForgottenArchitect.fbx     # Unity-ready FBX (generated)
│   ├── Textures/                  # Baked PBR textures (generated)
│   ├── Animations/                # Animation clips (generated)
│   └── Materials/                 # Material assets
├── Project/                       # Unity VRChat project
│   ├── Assets/
│   │   ├── ForgottenArchitect/
│   │   │   ├── ForgottenArchitect.prefab
│   │   │   ├── FX_Controller.controller
│   │   │   ├── ExpressionsMenu.asset
│   │   │   └── ExpressionParameters.asset
│   │   └── Scripts/
│   │       └── Editor/
│   │           └── SetupAvatar.cs
│   ├── Packages/
│   │   └── manifest.json          # Unity package dependencies (VRChat SDK)
│   └── ProjectSettings/
├── docs/
│   ├── screenshots/                        # Auto-generated preview images
│   │   ├── front.png
│   │   ├── back.png
│   │   ├── face.png
│   │   ├── pose1.png
│   │   └── pose2.png
│   ├── BAKING_OPTIMIZATION_REPORT.md       # Full 17-page texture baking analysis
│   └── BAKING_QUICK_REFERENCE.md           # Quick optimization guide (TL;DR)
├── README.md                               # This file (auto-updated)
└── CLAUDE.md                               # Development log and technical notes
```

### Pipeline Flow

```mermaid
graph TD
    A[Push to GitHub] --> B[GitHub Actions Trigger]
    B --> C[Install Blender]
    C --> D[Generate 3D Model]
    D --> E[Bake Textures]
    E --> F[Create Animations]
    F --> G[Export FBX]
    G --> H[Render Screenshots]
    H --> I[Install Unity]
    I --> J[Setup VRChat Project]
    J --> K[Update README]
    K --> L[Commit & Push]
    L --> M[Upload Artifacts]
```

---

## 🎨 Technical Specifications

### Model Stats (Target)

| Metric | Value |
|--------|-------|
| **Polygons** | ~30,000 tris |
| **Bones** | ~75 (Rigify humanoid) |
| **Materials** | 4 (Bronze, Ivory, Saffron Bronze, Amber Glow) |
| **Texture Resolution** | 1024x1024 (CI) / 2048x2048 (local) |
| **Textures Baked** | 12 of 24 objects (only procedural bronze) |
| **Animations** | 4 (1 idle + 3 emotes) |
| **VRChat Performance** | Good |

### Texture Maps

Each material includes:
- **Base Color**: Albedo/diffuse color
- **Normal Map**: Surface detail and bump information
- **Metallic**: Metallic vs. dielectric areas
- **Roughness**: Surface glossiness variation
- **Emission**: Self-illuminating areas (mechanical eye, runes)

### Animation Details

| Animation | Duration | Type | Description |
|-----------|----------|------|-------------|
| **Idle** | 4s loop | Looping | Subtle swaying, mechanical breathing, finger micro-movements |
| **Prayer Unfold** | 2s | Toggle | Arms raise from prayer to T-pose, blade-fingers separate |
| **Rise from Knees** | 3s | Toggle | Legs telescope from 1.8m kneeling to 2.4m standing |
| **Meditation Glitch** | 4s | Trigger | Head rotates 360° on segmented neck, halo spins |

---

## 🛠️ Customization

### Modifying the Model

Edit `scripts/blender/generate_avatar.py`:

```python
# Change avatar height
KNEELING_HEIGHT = 1.8  # Meters (default kneeling height)

# Adjust pose
# Search for "create_kneeling_pose()" to modify prayer position

# Modify colors
bsdf.inputs['Base Color'].default_value = (R, G, B, 1.0)
```

### Adding New Animations

1. Edit `scripts/blender/create_animations.py`
2. Add new function (e.g., `create_new_emote_animation()`)
3. Call it in `main()`
4. Update `scripts/unity/SetupAvatar.cs` to add parameter and transition

### Changing Materials

Edit material creation functions in `generate_avatar.py`:

```python
def create_material_bronze():
    # Modify bronze color, metallic, roughness values
    bsdf.inputs['Base Color'].default_value = (0.15, 0.09, 0.05, 1.0)  # Dark bronze
    bsdf.inputs['Metallic'].default_value = 0.95
    bsdf.inputs['Roughness'].default_value = 0.6

    # Adjust verdigris noise (green patina)
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 8.0  # Lower = larger patches
```

---

## 📚 Documentation

### Key Technologies

- **Blender 3.6 LTS**: 3D modeling, rigging, texturing, rendering
- **Rigify**: Automatic humanoid rigging addon
- **Unity 2022.3.22f1 LTS**: VRChat-compatible game engine
- **VRChat SDK3**: Avatar upload and expression system
- **GitHub Actions**: CI/CD automation
- **Python 3**: Scripting and automation

### VRChat SDK Integration

The avatar uses:
- `VRCAvatarDescriptor`: Main avatar component
- `VRCExpressionsMenu`: In-game emote menu
- `VRCExpressionParameters`: Avatar parameters (3 bools for emotes)
- FX Animator Layer: Custom animations and blending

### Performance Optimization

- **Polygon Budget**: Target 25-40k tris (Good rank)
- **Texture Atlasing**: Single material per mesh where possible
- **LOD**: Not implemented (could be added for better performance)
- **Skinned Mesh Renderers**: Minimize count (target: 1-2)
- **Material Slots**: Minimize count (target: 3-5)

---

## 🚀 CI/CD Pipeline Details

### GitHub Actions Workflow

The build pipeline (`build.yml`) runs on every push and performs:

1. **Environment Setup** (~5 min)
   - Ubuntu runner
   - Blender 3.6.5 installation
   - Unity 2022.3.22f1 installation

2. **Asset Generation** (~10-20 min)
   - Procedural model generation
   - Rigify humanoid rigging
   - Texture baking (Optimized: only bronze materials, 5-10 min instead of 2+ hours)
   - Animation creation
   - FBX export

3. **Unity Integration** (~10-20 min)
   - VRChat SDK installation
   - Avatar descriptor setup
   - FX animator configuration
   - Expressions menu creation
   - Prefab generation

4. **Documentation** (~5-10 min)
   - Screenshot rendering (5 views, 1920x1080)
   - README update with gallery
   - Build summary generation

5. **Artifact Archival**
   - Avatar package upload
   - Build logs upload
   - Git commit & push

### Caching Strategy

The pipeline uses GitHub Actions cache for:
- Blender installation (~300 MB)
- Unity installation (~2 GB)
- Package dependencies

This reduces build time from ~90 min → ~30 min on subsequent runs.

---

## 🧪 Testing Checklist

Before uploading to VRChat, verify:

- [ ] Avatar appears in Unity Scene view
- [ ] Humanoid rig is properly configured (Avatar Configuration)
- [ ] All materials have textures assigned
- [ ] FX Animator has all 3 emote parameters
- [ ] Expressions menu shows all 3 emotes
- [ ] Avatar Descriptor shows "Good" performance rank
- [ ] Test animations in Unity Animator window
- [ ] Viewpoint (eye position) is correctly placed
- [ ] No missing script errors in Console

---

## 📜 License

This project is released under **MIT License**.

You are free to:
- ✅ Use this avatar in VRChat
- ✅ Modify the code and design
- ✅ Create derivatives
- ✅ Use in commercial projects

**Attribution appreciated but not required!**

---

## 🙏 Credits

### Concept & Design
- **Elder Scrolls** (Bethesda): Dwemer aesthetic inspiration
- **H.P. Lovecraft**: Cosmic horror themes
- **Japanese Horror Cinema**: Yūrei and onryō aesthetics

### Tools & Technologies
- [Blender](https://www.blender.org/) - Open-source 3D creation suite
- [Unity](https://unity.com/) - Game engine
- [VRChat](https://hello.vrchat.com/) - Social VR platform
- [Rigify](https://docs.blender.org/manual/en/latest/addons/rigging/rigify/) - Blender rigging addon
- [GitHub Actions](https://github.com/features/actions) - CI/CD automation

### Created by
**Claude (Anthropic)** + **Human Collaboration**

This avatar and automation pipeline were designed by Claude (AI assistant) based on human requirements. All code, 3D generation scripts, and documentation are original works created for this project.

---

## 🐛 Known Issues

- [ ] Unity headless mode may fail on some GitHub Actions runners (use Unity Hub workaround)
- [ ] Blender Rigify generation can be slow in headless mode (~10-15 min)
- [ ] Screenshot rendering requires significant CPU time (consider GPU rendering in future)
- [ ] VRChat SDK installation via CLI still experimental (may require manual VCC install)
- [⚠️] **Texture baking optimization**: Debug version currently deployed with material detection fallback. Optimized script may skip all textures instead of baking bronze materials (investigating node persistence between scripts)

---

## 🗺️ Roadmap

### Future Enhancements

- [ ] **Quest Compatibility**: Mobile-optimized version with simplified shaders
- [ ] **Gesture Animations**: Finger pose-triggered horror effects
- [ ] **Audio Integration**: Mechanical grinding sounds, breathing ambiance
- [ ] **PhysBones**: Hair and cable tendril physics
- [ ] **Particle Effects**: Smoke/steam from mechanical joints
- [ ] **Blend Shapes**: Facial expressions (limited by half-masked face)
- [ ] **LOD System**: Multiple polygon levels for performance
- [ ] **Automatic Upload**: Direct VRChat upload from CI (if API available)

---

## 💬 Support

- **Issues**: [GitHub Issues](https://github.com/jakubkrzysztofsikora/Vrchat-avatar/issues)
- **Discussions**: [GitHub Discussions](https://github.com/jakubkrzysztofsikora/Vrchat-avatar/discussions)

---

<div align="center">

**🎭 The Forgotten Architect 🎭**

*"Some knowledge is best left buried in the mechanisms of the past."*

---

Made with 🤖 automation and ❤️ horror aesthetics

</div>
