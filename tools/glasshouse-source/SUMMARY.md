# DAYLIGHT GLASSHOUSE — asset delivery

Status: four original rendered assets created, decoded, visually inspected with vision_analyze, and verified. No website repository, deployment, profile, settings, credential, publishing or messaging work was performed. No browser or login process was started. Render processes have exited; a final process listing showed no remaining Blender, Mitsuba, uv or asset-render Python process.

## Final assets

All paths below are relative to /opt/data/home/silviya-glasshouse-assets/.

| File | Dimensions | Actual bytes | WebP quality |
| --- | --- | ---: | ---: |
| hero-glasshouse.webp | 1800 × 1200 | 188588 | 94 |
| sky-study.webp | 1400 × 1050 | 103304 | 94 |
| skin-ritual.webp | 1400 × 1050 | 92392 | 94 |
| quiet-growth.webp | 1400 × 1050 | 116522 | 94 |

Total final WebP payload, including embedded provenance: 500806 bytes. Each asset is below its individual 500000-byte hero / 400000-byte support limit. ASSET-MANIFEST.json contains exact byte counts, dimensions, SHA-256 hashes, English and Bulgarian alt text, intended use, crop guidance, render metadata, and source paths. Each WebP also has a full-filename-plus-.json provenance sidecar.

## Actual method and origin

These are original authored 3D illustrations, not AI photographs, not image-model outputs and not photographs of real products or locations. No connected image-generation tool was exposed by the CLI's one capability search. No credential files were opened and no keys were inspected.

Geometry was authored procedurally with Blender 5.2.2 LTS via isolated uv/bpy on Python 3.13. It includes curved lamina meshes with thickness, midribs and side veins, branching stems, fern pinnae, hollow revolved ceramic/glass vessels, mineral plinths and curved architectural screens. No stock geometry, image textures or external art assets were used. The mineral sphere texture is seeded multiscale procedural noise.

Two Cycles attempts exited 137 before producing an image. A read-only runtime check found a 4294967296-byte cgroup limit and an OOM kill; host free memory and available disk were not the renderer's effective memory budget. The second attempt reduced geometry resolution, render threads and tile size, but still could not complete in this shared container. The requested fallback was then used: export the original authored geometry to PLY and ray trace it with Mitsuba 3.9.1 LLVM CPU.

Final renderer: Mitsuba 3.9.1, 64 samples per pixel, maximum path depth 8, three Dr.Jit worker threads, 384-pixel cropped tiles, eight samples per pass. Explicit ACES-like display curve and sRGB encoding. Mild OpenCV non-local-means denoising (h=3, hColor=3, template=7, search=21); this is non-generative image-space cleanup, not Blender/OIDN denoising. Full-resolution PNG originals and linear float arrays are retained in source/.

Actual final render times from machine-generated render records:

- Hero: 76.31 seconds.
- Sky study: 44.68 seconds.
- Skin ritual: 45.03 seconds.
- Quiet growth: 41.79 seconds.

## Visual review and bounded correction

A low-resolution hero preview revealed two concrete defects in the fallback renderer: opaque architectural backfaces appeared black, and a light emitter was visible as a black panel. One correction pass made opaque materials two-sided and hid emitters from direct camera rays; the final full-resolution set was then rendered. The hero PNG and all four delivered WebPs were loaded with vision_analyze.

Observed final content:

- Hero: a substantial amber sphere, mineral pedestal, green branching leaves and fern, shallow water dish, curved cool-green architectural screen. No light-panel/backface defect remains.
- Sky: softly mottled mineral sphere, thick amber crescent, botanical branch and low glass lens. The crescent is an intentionally dreamlike suspended sculptural element, not an astronomical diagram.
- Skin: unlabelled ribbed frosted glass vessel, porcelain bowl/water, broad veined leaves and a small amber disk. No product branding or medical implication.
- Growth: ribbed spruce vase, generous mesh foliage and nested pale/amber vessels. No people or family portrait.

All four have coherent cool jade/spruce/green/amber materials and contain no text, logos or people. Foliage is real rendered geometry, not SVG or an image cutout.

Limitations: these read as stylized authored design-magazine 3D illustrations, not documentary photography. Some sampling grain remains in refractive glass/water and fine contact shadows, most visibly in the skin still life. The amber has a yellow-gold cast under daylight. Lighting is soft window-like studio daylight; there is no sharp architectural window-grid shadow or fully resolved refractive caustic pattern. Botanical forms are authored stylizations, not botanical species documentation. The lighting/tone-map means final pixels are not flat hex swatches. No further polish loop was run.

## Reproducible source

- source/render.py — complete procedural geometry authoring and the retained, unsuccessful Cycles execution path. Do not use its default Cycles entrypoint to reproduce final images in this container.
- source/export_scenes.py — build/evaluate original Blender meshes and export grouped PLYs and scene descriptions.
- source/render_mitsuba.py — the successful final renderer; generates the original mineral texture, tiled ray-traced images, linear arrays and render records.
- source/package_assets.py — embeds the authored-render brief/provenance in PNG text and WebP XMP, optimizes WebP, writes manifest and sidecars.
- source/verify_assets.py — decodes every asset, verifies dimensions/budgets/hashes/source links and reads embedded provenance back.
- source/reproduce.sh — isolated, pinned-dependency reproduction commands. Run with bash; no global installation is needed.
- source/dependencies.txt — actual Python-package versions used.
- source/ORIGIN.md — authored art direction and origin.
- source/*.blend — editable original authored scenes. Blender material graphs are source-design references, not pixel-identical substitutes for the Mitsuba shaders.
- source/geometry/*.ply and source/*-scene.json — reusable renderer inputs, sufficient to reproduce without running Blender.
- source/hero-glasshouse.png, source/sky-study.png, source/skin-ritual.png, source/quiet-growth.png — full-resolution PNG originals with embedded provenance.
- source/*-linear.npy — retained linear-light renders, prior to tone mapping/denoising.
- source/*-render.json, source/mitsuba-render.log and source/verification.json — actual execution evidence. Logs from failed Cycles attempts and the initial preview are retained separately and are not final assets.

## Commands actually executed

Working directory for every command: /opt/data/home/silviya-glasshouse-assets/.

Geometry export succeeded with exit 0:

    UV_CACHE_DIR="$PWD/.uv-cache" UV_PYTHON_INSTALL_DIR="$PWD/.uv-python" TMPDIR="$PWD/source" OMP_NUM_THREADS=3 OPENBLAS_NUM_THREADS=3 MALLOC_ARENA_MAX=2 uv run --no-project --python 3.13 --with bpy==5.2.2 python source/export_scenes.py > source/export.log 2>&1

Final rendering succeeded with exit 0:

    UV_CACHE_DIR="$PWD/.uv-cache" UV_PYTHON_INSTALL_DIR="$PWD/.uv-python" XDG_CACHE_HOME="$PWD/.cache" DRJIT_CACHE_DIR="$PWD/.drjit-cache" TMPDIR="$PWD/source" OMP_NUM_THREADS=3 OPENBLAS_NUM_THREADS=3 MALLOC_ARENA_MAX=2 uv run --no-project --python 3.13 --with mitsuba==3.9.1 --with pillow==12.3.0 --with numpy --with opencv-python-headless python source/render_mitsuba.py --scene all --samples 64 > source/mitsuba-render.log 2>&1

Packaging and verification both succeeded with exit 0:

    UV_CACHE_DIR="$PWD/.uv-cache" UV_PYTHON_INSTALL_DIR="$PWD/.uv-python" TMPDIR="$PWD/source" uv run --no-project --python 3.13 --with pillow==12.3.0 python source/package_assets.py
    UV_CACHE_DIR="$PWD/.uv-cache" UV_PYTHON_INSTALL_DIR="$PWD/.uv-python" TMPDIR="$PWD/source" uv run --no-project --python 3.13 --with mitsuba==3.9.1 --with pillow==12.3.0 --with numpy --with opencv-python-headless python source/verify_assets.py

The resolved versions were numpy 2.5.4, opencv-python-headless 5.0.0.93, Dr.Jit 1.5.0, Mitsuba 3.9.1 and Pillow 12.3.0. source/reproduce.sh pins the resolved NumPy and OpenCV versions too. For future complete reproduction:

    bash /opt/data/home/silviya-glasshouse-assets/source/reproduce.sh

The complete reproduction wrapper was authored after successful equivalent commands; it was not unnecessarily rerun to duplicate the rendering.

## Integration boundary

The coding worker can copy the four root WebPs into the website's assets directory and use manifest alt text/crop notes. Keep source/, caches, logs and editable scene files out of the deployed website. Preserve WebP XMP or retain its manifest/sidecar provenance if further processing strips metadata. This task did not edit, send, publish or deploy the website.
