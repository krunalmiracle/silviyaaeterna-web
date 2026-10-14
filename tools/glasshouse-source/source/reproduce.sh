#!/usr/bin/env bash
# Reproduce only within this asset directory; no global package installation.
set -euo pipefail
cd "$(dirname "$0")/.."
export UV_CACHE_DIR="$PWD/.uv-cache"
export UV_PYTHON_INSTALL_DIR="$PWD/.uv-python"
export XDG_CACHE_HOME="$PWD/.cache"
export DRJIT_CACHE_DIR="$PWD/.drjit-cache"
export TMPDIR="$PWD/source"
export OMP_NUM_THREADS=3
export OPENBLAS_NUM_THREADS=3
export MALLOC_ARENA_MAX=2
# Skip Blender for routine re-renders: committed PLY and scene JSON files suffice.
# To rebuild geometry too, run:
# uv run --no-project --python 3.13 --with bpy==5.2.2 python source/export_scenes.py
uv run --no-project --python 3.13 --with mitsuba==3.9.1 --with pillow==12.3.0 --with numpy==2.5.4 --with opencv-python-headless==5.0.0.93 python source/render_mitsuba.py --scene all --samples 64
uv run --no-project --python 3.13 --with pillow==12.3.0 python source/package_assets.py
uv run --no-project --python 3.13 --with mitsuba==3.9.1 --with pillow==12.3.0 --with numpy==2.5.4 --with opencv-python-headless==5.0.0.93 python source/verify_assets.py
