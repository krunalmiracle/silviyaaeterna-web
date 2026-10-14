# Original glasshouse renderer source

These are unchanged source snapshots from /opt/data/home/silviya-glasshouse-assets/. The complete local source archive remains there, including editable .blend scenes, evaluated PLY geometry, scene JSON, full PNG and linear-light render originals, render records and logs. It is a local directory, not a remotely hosted archive or a deployed endpoint.

The website retains only the eight small source/dependency/origin files under source/, four WebP provenance sidecars and the producer SUMMARY.md. No meshes, .blend files, environments, caches or render logs are included. Production serves none of tools/.

## Correct reproduction path

Final pixels came from Blender procedural geometry -> export_scenes.py PLY/scene export -> render_mitsuba.py CPU path tracing -> package_assets.py. render.py also retains a failed Cycles entrypoint; that entrypoint did not produce the final images and must not be presented as the renderer.

The scripts derive asset root from their own path: source/script.py resolves its parent's parent as root and reads root/source/. reproduce.sh likewise changes into its parent's parent. This snapshot preserves that layout. It is not a ready-to-run renderer until geometry and scene descriptions are restored or regenerated.

To reproduce in a separate scratch directory (not inside the website checkout):

1. Copy this directory's contents into the scratch asset root, retaining source/.
2. Either copy source/geometry/ and source/*-scene.json from the complete original archive, or regenerate them with the geometry-export command below. Verification also expects the original editable .blend sources; a fresh geometry export creates these.
3. Run the pinned reproduction script. It writes renders, WebPs and a new manifest into the scratch root; it does not deploy the site.

From the scratch asset root, geometry regeneration:

    uv run --no-project --python 3.13 --with bpy==5.2.2 python source/export_scenes.py

Then:

    bash source/reproduce.sh

The equivalent individual commands completed successfully in the original asset root, as recorded in SUMMARY.md. The wrapper was authored afterward and was not re-run for this integration. This integration only verified hashes/dimensions/provenance and copied the existing final WebPs; it did not repeat the expensive rendering.

For an in-place re-render of the complete original archive, the producer documents:

    bash /opt/data/home/silviya-glasshouse-assets/source/reproduce.sh

Do not execute reproduction casually on the shared website host. The website only requires the final local WebPs and static files, not these dependencies.
