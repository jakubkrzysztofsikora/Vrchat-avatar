#!/bin/bash
# Test script to verify Blender avatar generation works locally
# This simulates the GitHub Actions environment

set -e

echo "=== Testing Blender Avatar Generation (V4 Architecture) ==="
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "Docker not found. Please install Docker to run this test."
    exit 1
fi

# Create test directory
TEST_DIR="/tmp/vrchat-avatar-test-$(date +%s)"
mkdir -p "$TEST_DIR"

echo "Test directory: $TEST_DIR"
echo ""

# Copy scripts to test directory
cp -r scripts "$TEST_DIR/"
mkdir -p "$TEST_DIR/Avatar/BaseMeshes"
mkdir -p "$TEST_DIR/Avatar/Kitbash"

# Run Blender in Docker container (Ubuntu 24.04)
echo "Running Blender avatar generation in Docker..."
echo ""

docker run --rm \
    -v "$TEST_DIR:/work" \
    -w /work \
    ubuntu:24.04 \
    bash -c "
        set -e
        echo '1. Installing dependencies...'
        apt-get update -qq
        apt-get install -y -qq wget xz-utils > /dev/null 2>&1

        echo '2. Downloading Blender 3.6.5...'
        wget -q https://download.blender.org/release/Blender3.6/blender-3.6.5-linux-x64.tar.xz

        echo '3. Extracting Blender...'
        tar -xf blender-3.6.5-linux-x64.tar.xz

        echo '4. Generating base mesh (V4 - Skin Modifier)...'
        ./blender-3.6.5-linux-x64/blender --background --enable-autoexec --python scripts/blender/generate_basemesh.py

        echo ''
        echo '5. Generating kitbash assets...'
        ./blender-3.6.5-linux-x64/blender --background --enable-autoexec --python scripts/blender/generate_kitbash_assets.py

        echo ''
        echo '6. Generating avatar model (V4 - kitbash import)...'
        ./blender-3.6.5-linux-x64/blender --background --enable-autoexec --python scripts/blender/generate_avatar_v3.py

        echo ''
        echo '7. Checking output files...'

        if [ -f 'Avatar/BaseMeshes/PenitentMechanism_Base.blend' ]; then
            echo '✅ Base mesh created!'
            ls -lh Avatar/BaseMeshes/
        else
            echo '❌ Base mesh NOT created!'
            exit 1
        fi

        if [ -d 'Avatar/Kitbash' ] && ls Avatar/Kitbash/*.blend 1> /dev/null 2>&1; then
            echo '✅ Kitbash assets created!'
            ls -lh Avatar/Kitbash/
        else
            echo '❌ Kitbash assets NOT created!'
            exit 1
        fi

        if [ -f 'Avatar/ForgottenArchitect.blend' ]; then
            echo '✅ Avatar blend file created successfully!'
            ls -lh Avatar/ForgottenArchitect.blend
        else
            echo '❌ Avatar blend file NOT created!'
            exit 1
        fi
    "

RESULT=$?

if [ $RESULT -eq 0 ]; then
    echo ""
    echo "=== ✅ Test PASSED ==="
    echo "Avatar generation works correctly with V4 architecture!"
    echo ""
    echo "Generated files:"
    echo "  - Base mesh: $TEST_DIR/Avatar/BaseMeshes/PenitentMechanism_Base.blend"
    echo "  - Kitbash: $TEST_DIR/Avatar/Kitbash/*.blend"
    echo "  - Avatar: $TEST_DIR/Avatar/ForgottenArchitect.blend"
    echo ""
    echo "Clean up test directory with:"
    echo "  rm -rf $TEST_DIR"
else
    echo ""
    echo "=== ❌ Test FAILED ==="
    echo "Check logs above for errors"
    echo "Test directory preserved at: $TEST_DIR"
    exit 1
fi
