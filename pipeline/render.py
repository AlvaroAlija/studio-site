#!/usr/bin/env python3
"""Headless Blender render job for the workstation runner.

Renders a .blend scene to PNG via the Blender CLI. Meant to be invoked by the
`render.yml` self-hosted workflow (or by hand), then chained into upload.py:

    python3 pipeline/render.py --scene scenes/kelp-cathedral.blend --out out/kelp-cathedral.png
    python3 pipeline/upload.py --slug kelp-cathedral --image out/kelp-cathedral.png ...
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_BLENDER = "blender"


def find_blender(explicit: str | None) -> str:
    """Resolve the Blender executable, failing early with a clear message."""
    candidate = explicit or DEFAULT_BLENDER
    resolved = shutil.which(candidate)
    if resolved is None:
        raise FileNotFoundError(
            f"Blender executable not found: {candidate!r}. "
            "Install Blender or pass --blender /path/to/blender."
        )
    return resolved


def render(scene: Path, out: Path, blender: str, samples: int | None) -> None:
    """Render `scene` to `out` (PNG) using Blender in background mode."""
    if not scene.is_file():
        raise FileNotFoundError(f"Scene file does not exist: {scene}")
    out.parent.mkdir(parents=True, exist_ok=True)

    # Blender appends frame numbers; render to a padded path then normalise.
    cmd = [
        blender,
        "--background",
        str(scene),
        "--render-output", str(out.with_suffix("")) + "_####",
        "--render-format", "PNG",
    ]
    if samples is not None:
        expr = f"import bpy; bpy.context.scene.cycles.samples = {int(samples)}"
        cmd += ["--python-expr", expr]
    cmd += ["--render-frame", "1"]

    subprocess.run(cmd, check=True)

    rendered = out.parent / (out.stem + "_0001.png")
    if not rendered.is_file():
        raise RuntimeError(f"Blender finished but output frame is missing: {rendered}")
    rendered.replace(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene", required=True, type=Path, help="Path to the .blend scene")
    parser.add_argument("--out", required=True, type=Path, help="Output PNG path")
    parser.add_argument("--blender", default=None, help="Blender executable (default: blender on PATH)")
    parser.add_argument("--samples", type=int, default=None, help="Override Cycles sample count")
    args = parser.parse_args()

    try:
        blender = find_blender(args.blender)
        render(args.scene, args.out, blender, args.samples)
    except (FileNotFoundError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as exc:
        print(f"error: Blender exited with status {exc.returncode}", file=sys.stderr)
        return exc.returncode or 1

    print(f"rendered {args.scene} -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
