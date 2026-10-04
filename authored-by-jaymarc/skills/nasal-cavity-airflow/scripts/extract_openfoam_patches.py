#!/usr/bin/env python3
"""Split a sealed nasal-airway STL into OpenFOAM surface patches.

Coordinate frame (Pharyvac VG geometry, RAS mm):
  x = left-right, y = anterior-posterior (low y = nares), z = sup-inf

Exports: wall.stl, inletLeft.stl, inletRight.stl, outlet.stl
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import trimesh


def classify_faces(mesh: trimesh.Trimesh, y_tol: float, n_tol: float, x_mid: float | None):
    fc = mesh.triangles_center
    fn = mesh.face_normals
    y_min, y_max = mesh.bounds[0][1], mesh.bounds[1][1]
    if x_mid is None:
        x_mid = float(np.median(fc[:, 0]))

    inlet = (np.abs(fc[:, 1] - y_min) < y_tol) & (fn[:, 1] < -n_tol)
    outlet = (np.abs(fc[:, 1] - y_max) < y_tol) & (fn[:, 1] > n_tol)
    walls = ~(inlet | outlet)
    left = inlet & (fc[:, 0] < x_mid)
    right = inlet & (fc[:, 0] >= x_mid)
    return {
        "wall": walls,
        "inletLeft": left,
        "inletRight": right,
        "outlet": outlet,
        "meta": {
            "y_inlet_mm": float(y_min),
            "y_outlet_mm": float(y_max),
            "x_mid_mm": float(x_mid),
            "y_tol_mm": y_tol,
            "n_tol": n_tol,
        },
    }


def area_cm2(mesh: trimesh.Trimesh, mask: np.ndarray) -> float:
    return float(mesh.area_faces[mask].sum() / 100.0)


def export_submesh(mesh: trimesh.Trimesh, mask: np.ndarray, path: Path) -> None:
    idx = np.where(mask)[0]
    if len(idx) == 0:
        raise RuntimeError(f"No faces to export: {path.name}")
    sub = mesh.submesh([idx], append=True)
    sub.export(path)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("stl", type=Path)
    ap.add_argument("out_dir", type=Path)
    ap.add_argument("--y-tol", type=float, default=2.0)
    ap.add_argument("--n-tol", type=float, default=0.7)
    ap.add_argument("--x-mid", type=float, default=None)
    args = ap.parse_args()

    mesh = trimesh.load(args.stl, force="mesh")
    if not mesh.is_watertight:
        raise SystemExit(f"STL not watertight: {args.stl}")

    masks = classify_faces(mesh, args.y_tol, args.n_tol, args.x_mid)
    meta = masks.pop("meta")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "source": str(args.stl.resolve()),
        "watertight": True,
        "volume_cm3": float(mesh.volume / 1000.0),
        "bbox_mm": mesh.bounds.tolist(),
        **meta,
        "patches_cm2": {},
    }

    for name, mask in masks.items():
        report["patches_cm2"][name] = area_cm2(mesh, mask)
        export_submesh(mesh, mask, args.out_dir / f"{name}.stl")

    (args.out_dir / "patch_report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
